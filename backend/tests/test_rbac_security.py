"""Security-focused API tests: privilege escalation, protected-role guards,
last-admin protection and cross-tenant isolation."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.rbac.constants import RBAC_PERMISSIONS
from apps.rbac.models import Permission, Role, RolePermission, UserRoleAssignment
from apps.rbac.services import RoleAssignmentService, RoleService
from tests.factories import RoleFactory, UserFactory

pytestmark = pytest.mark.django_db

API = "/api/v1/rbac"


def _client_for(user, tenant) -> APIClient:
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        HTTP_X_TENANT_ID=str(tenant.pk),
    )
    return client


def _role_with(tenant, code: str, codes: list[str]) -> Role:
    role = RoleFactory(tenant=tenant, code=code)
    for code_ in codes:
        RolePermission.objects.create(role=role, permission=Permission.objects.get(code=code_), allow=True)
    return role


def _assign(user, role: Role) -> None:
    user.tenants.add(role.tenant)
    RoleAssignmentService().assign(user=user, role=role, actor=None, reason="test")


class TestMemberRestrictions:
    def test_member_cannot_manage_roles(self, tenant_authenticated_client):
        assert tenant_authenticated_client.get(f"{API}/roles/").status_code == 403

    def test_member_cannot_view_matrix(self, tenant_authenticated_client):
        assert tenant_authenticated_client.get(f"{API}/matrix/").status_code == 403

    def test_member_cannot_view_assignments(self, tenant_authenticated_client):
        assert tenant_authenticated_client.get(f"{API}/assignments/").status_code == 403

    def test_member_cannot_view_groups(self, tenant_authenticated_client):
        assert tenant_authenticated_client.get(f"{API}/groups/").status_code == 403

    def test_member_cannot_view_permissions(self, tenant_authenticated_client):
        assert tenant_authenticated_client.get(f"{API}/permissions/").status_code == 403


class TestEscalation:
    def test_escalation_blocked_via_api(self, tenant):
        actor = UserFactory()
        target = UserFactory()
        _assign(actor, _role_with(tenant, "assigner", [RBAC_PERMISSIONS["ASSIGNMENT_CREATE"]]))
        broad = _role_with(tenant, "broad", [RBAC_PERMISSIONS["ROLE_CREATE"], RBAC_PERMISSIONS["ROLE_DELETE"]])

        client = _client_for(actor, tenant)
        response = client.post(
            f"{API}/assignments/",
            {"user": str(target.pk), "role": str(broad.pk), "reason": "power-grab"},
            format="json",
        )
        assert response.status_code == 403
        assert response.json()["errors"][0]["code"] == "privilege_escalation"

    def test_escalation_guard_can_be_disabled(self, tenant, settings):
        settings.RBAC_ENFORCE_ESCALATION_GUARD = False
        actor = UserFactory()
        target = UserFactory()
        _assign(actor, _role_with(tenant, "assigner", [RBAC_PERMISSIONS["ASSIGNMENT_CREATE"]]))
        broad = _role_with(tenant, "broad", [RBAC_PERMISSIONS["ROLE_CREATE"]])

        client = _client_for(actor, tenant)
        response = client.post(
            f"{API}/assignments/",
            {"user": str(target.pk), "role": str(broad.pk)},
            format="json",
        )
        assert response.status_code == 201

    def test_subset_grant_allowed_via_api(self, tenant):
        actor = UserFactory()
        target = UserFactory()
        _assign(actor, _role_with(tenant, "assigner", [RBAC_PERMISSIONS["ASSIGNMENT_CREATE"], "catalog.item.read"]))
        cashier = _role_with(tenant, "cashier", ["catalog.item.read"])

        client = _client_for(actor, tenant)
        response = client.post(
            f"{API}/assignments/",
            {"user": str(target.pk), "role": str(cashier.pk), "reason": "hired"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["data"]["role_code"] == "cashier"


class TestProtectedGuards:
    def test_protected_role_code_locked_via_api(self, rbac_admin_client, tenant):
        admin = Role.objects.get(tenant=tenant, code="admin")
        response = rbac_admin_client.patch(f"{API}/roles/{admin.pk}/", {"code": "super_admin"}, format="json")
        assert response.status_code == 409
        assert response.json()["errors"][0]["code"] == "protected_role"

    def test_last_admin_cannot_be_revoked_via_api(self, rbac_admin_client, rbac_admin_user, tenant):
        admin = Role.objects.get(tenant=tenant, code="admin")
        assignment = UserRoleAssignment.objects.get(user=rbac_admin_user, role=admin, tenant=tenant, is_active=True)
        response = rbac_admin_client.delete(f"{API}/assignments/{assignment.pk}/")
        assert response.status_code == 409
        assert response.json()["errors"][0]["code"] == "protected_assignment"

    def test_second_admin_can_revoke_via_api(self, rbac_admin_client, rbac_admin_user, tenant):
        admin = Role.objects.get(tenant=tenant, code="admin")
        second = UserFactory()
        second.tenants.add(tenant)
        RoleAssignmentService().assign(user=second, role=admin, actor=None)
        assignment = UserRoleAssignment.objects.get(user=rbac_admin_user, role=admin, tenant=tenant, is_active=True)
        response = rbac_admin_client.delete(f"{API}/assignments/{assignment.pk}/")
        assert response.status_code == 204

    def test_assigning_protected_role_requires_privilege(self, tenant):
        actor = UserFactory()
        target = UserFactory()
        _assign(actor, _role_with(tenant, "assigner", [RBAC_PERMISSIONS["ASSIGNMENT_CREATE"]]))
        admin = Role.objects.get(tenant=tenant, code="admin")

        client = _client_for(actor, tenant)
        response = client.post(
            f"{API}/assignments/",
            {"user": str(target.pk), "role": str(admin.pk)},
            format="json",
        )
        assert response.status_code == 409
        assert response.json()["errors"][0]["code"] == "protected_role"


class TestTenantIsolation:
    def test_role_invisible_across_tenants(self, rbac_admin_client, tenant):
        from tests.factories import TenantFactory

        other = TenantFactory()
        foreign = RoleFactory(tenant=other, code="foreign")
        response = rbac_admin_client.get(f"{API}/roles/{foreign.pk}/")
        assert response.status_code == 404

    def test_matrix_rejects_foreign_role(self, rbac_admin_client, tenant):
        from tests.factories import TenantFactory

        other = TenantFactory()
        foreign = RoleFactory(tenant=other, code="foreign")
        response = rbac_admin_client.get(f"{API}/matrix/?role={foreign.pk}")
        assert response.status_code == 404

    def test_cross_tenant_parent_link_rejected(self, rbac_admin_client, tenant):
        from tests.factories import TenantFactory

        other = TenantFactory()
        foreign = RoleFactory(tenant=other, code="foreign")
        member = Role.objects.get(tenant=tenant, code="member")
        response = rbac_admin_client.post(
            f"{API}/roles/{member.pk}/parents/", {"parent_role": str(foreign.pk)}, format="json"
        )
        assert response.status_code == 422
        assert response.json()["errors"][0]["code"] == "cross_tenant_reference"


class TestRoleDeletionGuards:
    def test_role_with_assignments_cannot_be_deleted(self, rbac_admin_client, tenant):
        member = Role.objects.get(tenant=tenant, code="member")
        target = UserFactory()
        target.tenants.add(tenant)
        RoleAssignmentService().assign(user=target, role=member, actor=None)

        response = rbac_admin_client.delete(f"{API}/roles/{member.pk}/")
        assert response.status_code == 409
        assert response.json()["errors"][0]["code"] == "role_in_use"
        assert Role.objects.filter(pk=member.pk).exists()

    def test_inactive_role_cannot_be_assigned(self, tenant):
        from tests.factories import UserFactory as UF

        actor = UF()
        target = UF()
        _assign(actor, _role_with(tenant, "assigner", [RBAC_PERMISSIONS["ASSIGNMENT_CREATE"]]))
        inactive = RoleService().create({"tenant": tenant, "name": "Retired", "code": "retired"})
        Role.objects.filter(pk=inactive.pk).update(is_active=False)
        inactive.refresh_from_db()

        client = _client_for(actor, tenant)
        response = client.post(
            f"{API}/assignments/",
            {"user": str(target.pk), "role": str(inactive.pk)},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["errors"][0]["code"] == "role_inactive"
