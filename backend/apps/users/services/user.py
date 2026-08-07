"""Enterprise User Service managing user accounts, profiles, role assignments, and branch scoping."""

from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.core.models.user import UserStatus
from apps.rbac.repositories import RoleRepository
from apps.rbac.services.assignment import RoleAssignmentService
from apps.users.exceptions import BranchCompanyMismatchError, DuplicateUserEmailError, UserDeleteForbiddenError
from apps.users.models import EmployeeProfile
from apps.users.repositories import EmployeeProfileRepository, UserRepository

logger = logging.getLogger(__name__)
User = get_user_model()


class UserService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.profile_repository = EmployeeProfileRepository()
        self.role_assignment_service = RoleAssignmentService()
        self.role_repository = RoleRepository()

    @transaction.atomic
    def create_enterprise_user(
        self,
        tenant,
        company,
        primary_branch,
        *,
        email: str,
        first_name: str,
        last_name: str = "",
        password: str | None = None,
        username: str | None = None,
        phone: str = "",
        employee_number: str = "",
        arabic_name: str = "",
        english_name: str = "",
        job_title: str = "",
        department: str = "",
        roles: list | None = None,
        branches: list | None = None,
        manager=None,
        **profile_fields,
    ) -> User:
        clean_email = email.lower().strip()
        if User.objects.filter(email=clean_email, is_deleted=False).exists():
            raise DuplicateUserEmailError(f"A user with email '{clean_email}' already exists.")

        if company and company.tenant_id != tenant.pk:
            raise BranchCompanyMismatchError("Company does not belong to the current tenant.")

        if primary_branch and company and primary_branch.company_id != company.pk:
            raise BranchCompanyMismatchError("Primary branch does not belong to the specified company.")

        user = User.objects.create_user(
            email=clean_email,
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone=phone,
            password=password or "Password123!",
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        user.tenants.add(tenant)

        profile = self.profile_repository.create(
            user=user,
            tenant=tenant,
            company=company,
            primary_branch=primary_branch,
            employee_number=employee_number,
            arabic_name=arabic_name,
            english_name=english_name or f"{first_name} {last_name}".strip(),
            job_title=job_title,
            department=department,
            manager=manager,
            **profile_fields,
        )

        if primary_branch:
            profile.branches.add(primary_branch)
        if branches:
            for b in branches:
                if b.company_id == company.pk:
                    profile.branches.add(b)

        # Assign initial roles if provided
        if roles:
            for role_obj in roles:
                self.role_assignment_service.assign(
                    user=user,
                    role=role_obj,
                )

        logger.info("Created enterprise user %s for tenant %s company %s", user.email, tenant.slug, company.code if company else "N/A")
        return user

    @transaction.atomic
    def update_user_and_profile(self, user: User, *, user_fields: dict | None = None, profile_fields: dict | None = None) -> User:
        if user_fields:
            for k, v in user_fields.items():
                if hasattr(user, k):
                    setattr(user, k, v)
            user.save()

        if profile_fields and hasattr(user, "employee_profile"):
            profile = user.employee_profile
            for k, v in profile_fields.items():
                if hasattr(profile, k):
                    setattr(profile, k, v)
            profile.save()

        return user

    @transaction.atomic
    def activate_user(self, user: User) -> User:
        user.activate()
        logger.info("Activated user %s", user.email)
        return user

    @transaction.atomic
    def deactivate_user(self, user: User) -> User:
        user.deactivate()
        logger.info("Deactivated user %s", user.email)
        return user

    @transaction.atomic
    def lock_user(self, user: User) -> User:
        user.lock_account()
        logger.info("Locked user %s", user.email)
        return user

    @transaction.atomic
    def unlock_user(self, user: User) -> User:
        user.unlock_account()
        logger.info("Unlocked user %s", user.email)
        return user

    @transaction.atomic
    def reset_password(self, user: User, new_password: str) -> User:
        user.set_password(new_password)
        user.save(update_fields=["password", "password_changed_at", "updated_at"])
        logger.info("Reset password for user %s", user.email)
        return user

    @transaction.atomic
    def assign_role(self, user: User, role, tenant) -> None:
        self.role_assignment_service.assign(user=user, role=role)

    @transaction.atomic
    def revoke_role(self, user: User, role, tenant) -> None:
        self.role_assignment_service.revoke(user=user, role=role)

    @transaction.atomic
    def assign_branch(self, user: User, branch) -> User:
        if hasattr(user, "employee_profile"):
            user.employee_profile.branches.add(branch)
        return user

    @transaction.atomic
    def transfer_primary_branch(self, user: User, new_branch) -> User:
        if hasattr(user, "employee_profile"):
            profile = user.employee_profile
            profile.primary_branch = new_branch
            profile.branches.add(new_branch)
            profile.save(update_fields=["primary_branch", "updated_at"])
        return user

    @transaction.atomic
    def soft_delete_user(self, user: User) -> User:
        # Check active dependencies guard
        has_sales = getattr(user, "sales", None) and user.sales.filter(is_deleted=False).exists()
        has_prescriptions = getattr(user, "prescriptions", None) and user.prescriptions.filter(is_deleted=False).exists()

        if has_sales or has_prescriptions:
            raise UserDeleteForbiddenError("Cannot delete user with active sales or prescription records.")

        user.delete()
        logger.info("Soft deleted user %s", user.email)
        return user
