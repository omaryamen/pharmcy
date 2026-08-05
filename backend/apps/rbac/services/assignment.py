"""User ↔ role assignment service.

Assigning or revoking a role is a privileged operation with two safety nets:

- **Escalation guard**: an actor may only grant a role whose effective
  granted permissions are a subset of the actor's own effective permissions
  (superusers and system bootstrap are exempt).
- **Protected-role guard**: protected roles may only be touched by actors who
  hold ``rbac.role.protected_manage``.
- **Last-admin guard**: the final active ``admin`` assignment for a tenant
  can never be revoked, so a tenant cannot lock itself out.
"""

from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.common.exceptions import ConflictError, NotFoundError
from apps.common.services.base import BaseService
from apps.common.utils.context import get_current_user

from ..constants import ADMIN_ROLE_CODE, RBAC_PERMISSIONS
from ..engine import PermissionCache, PermissionEngine, PermissionResolver
from ..exceptions import (
    InactiveRoleError,
    MissingRbacPermissionError,
    PrivilegeEscalationError,
    ProtectedAssignmentError,
    ProtectedRoleError,
)
from ..models import Role, UserRoleAssignment
from ..repositories import UserRoleAssignmentRepository


class RoleAssignmentService(BaseService[UserRoleAssignment]):
    model = UserRoleAssignment
    repository_class = UserRoleAssignmentRepository

    def __init__(self, repository: UserRoleAssignmentRepository | None = None) -> None:
        super().__init__(repository)
        self.engine = PermissionEngine()
        self.resolver = PermissionResolver()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def list_for_user(self, user, tenant) -> list[UserRoleAssignment]:
        return self.repository.active_for_user(user, tenant)

    def active_roles_for_user(self, user, tenant) -> list[Role]:
        return [assignment.role for assignment in self.repository.active_for_user(user, tenant)]

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------
    @transaction.atomic
    def assign(self, *, user, role: Role, actor=None, is_primary: bool = False, reason: str = "") -> UserRoleAssignment:
        actor = actor or get_current_user()
        tenant = role.tenant

        if not role.is_active:
            raise InactiveRoleError()
        if not user.tenants.filter(pk=tenant.pk).exists():
            raise ConflictError("User is not a member of this tenant.")

        self._assert_can(RBAC_PERMISSIONS["ASSIGNMENT_CREATE"], actor, tenant)
        self._assert_role_assignable(role, actor)
        self._assert_no_escalation(role, actor)

        assignment = self.repository.get_any(tenant=tenant, user=user, role=role)
        if assignment is None:
            assignment = self.repository.create(
                tenant=tenant,
                user=user,
                role=role,
                is_primary=is_primary,
                is_active=True,
                reason=reason,
            )
        else:
            if assignment.is_active:
                assignment = self.repository.update(
                    assignment, is_primary=is_primary or assignment.is_primary, reason=reason or assignment.reason
                )
            else:
                assignment = self.repository.update(
                    assignment, is_active=True, is_primary=is_primary, reason=reason
                )

        if is_primary:
            self.repository.demote_primaries(user, tenant, except_assignment=assignment)
            self.repository.update(assignment, is_primary=True)

        PermissionCache().invalidate()
        return assignment

    @transaction.atomic
    def revoke(self, *, user, role: Role, actor=None, reason: str = "") -> UserRoleAssignment:
        actor = actor or get_current_user()
        tenant = role.tenant
        self._assert_can(RBAC_PERMISSIONS["ASSIGNMENT_DELETE"], actor, tenant)
        self._assert_role_assignable(role, actor)

        assignment = self.repository.get_active(tenant=tenant, user=user, role=role)
        if assignment is None:
            raise NotFoundError("No active assignment found for this user and role.")

        self._assert_last_admin_safe(tenant, role, assignment)
        assignment = self.repository.update(assignment, is_active=False, reason=reason or assignment.reason)
        if assignment.is_primary:
            self.repository.demote_primaries(user, tenant)

        PermissionCache().invalidate()
        return assignment

    @transaction.atomic
    def set_user_roles(self, *, user, tenant, role_codes: list[str], actor=None, reason: str = "") -> dict:
        """Replace a user's active roles with exactly ``role_codes``."""
        actor = actor or get_current_user()
        desired: list[Role] = []
        for code in role_codes:
            role = Role.objects.filter(tenant=tenant, code=code).first()
            if role is None:
                raise ConflictError(f"Role '{code}' does not exist in this tenant.")
            desired.append(role)

        current = self.repository.active_for_user(user, tenant)
        current_roles = {assignment.role for assignment in current}
        desired_set = set(desired)

        assigned = []
        for role in desired_set:
            assignment = self.assign(user=user, role=role, actor=actor, reason=reason)
            assigned.append(assignment.role.code)
        for assignment in current:
            if assignment.role not in desired_set:
                self.revoke(user=user, role=assignment.role, actor=actor, reason=reason)

        return {"assigned": sorted(set(assigned)), "removed": sorted(r.code for r in current_roles - desired_set)}

    @transaction.atomic
    def bulk_assign(self, entries: list[dict], actor=None) -> dict:
        """Assign several (user, role) pairs in one transaction."""
        actor = actor or get_current_user()
        assigned: list[str] = []
        errors: list[dict] = []
        for entry in entries:
            try:
                assignment = self.assign(user=entry["user"], role=entry["role"], actor=actor, reason=entry.get("reason", ""))
                assigned.append(str(assignment.pk))
            except Exception as exc:  # noqa: BLE001 - collect per-entry failures
                errors.append({"user": str(entry.get("user", "")), "role": str(entry.get("role", "")), "error": str(exc)})
        return {"assigned": assigned, "errors": errors}

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------
    def _assert_can(self, code: str, actor, tenant) -> None:
        if actor is None or actor.is_superuser or not getattr(actor, "is_authenticated", False):
            return
        if not self.engine.has_permission(actor, code, tenant):
            raise MissingRbacPermissionError(f"Permission '{code}' is required.")

    def _assert_role_assignable(self, role: Role, actor) -> None:
        if role.is_protected:
            if actor is None or actor.is_superuser:
                return
            if not self.engine.has_permission(actor, RBAC_PERMISSIONS["ROLE_PROTECTED_MANAGE"], role.tenant):
                raise ProtectedRoleError()

    def _assert_no_escalation(self, role: Role, actor) -> None:
        if actor is None or actor.is_superuser or not settings.RBAC_ENFORCE_ESCALATION_GUARD:
            return
        actor_codes = self.engine.effective_permissions(actor, role.tenant)
        granted = {code for code, (allow, _src) in self.resolver.role_permission_map(role).items() if allow}
        missing = granted - actor_codes
        if missing:
            raise PrivilegeEscalationError(missing)

    def _assert_last_admin_safe(self, tenant, role: Role, assignment: UserRoleAssignment) -> None:
        if role.code == ADMIN_ROLE_CODE or role.is_protected:
            active_admin_count = self.repository.count_active_admins(tenant, ADMIN_ROLE_CODE)
            if active_admin_count <= 1:
                raise ProtectedAssignmentError()
