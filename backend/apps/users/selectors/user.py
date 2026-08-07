"""User selector functions for tenant, company, branch, and role-scoped queries."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from apps.users.repositories import EmployeeProfileRepository, UserRepository

User = get_user_model()


class UserSelector:
    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.profile_repository = EmployeeProfileRepository()

    def list_users(
        self,
        tenant,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> QuerySet[User]:
        qs = User.objects.filter(tenants=tenant).select_related("employee_profile", "employee_profile__company", "employee_profile__primary_branch")

        if company_id:
            qs = qs.filter(employee_profile__company_id=company_id)
        if branch_id:
            qs = qs.filter(employee_profile__branches__id=branch_id)
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(first_name__icontains=search) | qs.filter(last_name__icontains=search) | qs.filter(employee_profile__employee_number__icontains=search)
        return qs.distinct()

    def get_user_detail(self, tenant, user_id) -> User | None:
        return (
            User.objects.filter(tenants=tenant, pk=user_id)
            .select_related(
                "employee_profile",
                "employee_profile__company",
                "employee_profile__primary_branch",
                "employee_profile__manager",
                "employee_profile__direct_supervisor",
            )
            .prefetch_related("employee_profile__branches", "role_assignments", "role_assignments__role")
            .first()
        )

    def get_user_stats(self, tenant) -> dict[str, Any]:
        total_users = User.objects.filter(tenants=tenant).count()
        active_users = User.objects.filter(tenants=tenant, is_active=True).count()
        locked_users = User.objects.filter(tenants=tenant, status="locked").count()
        return {
            "tenant_id": str(tenant.pk),
            "total_users": total_users,
            "active_users": active_users,
            "locked_users": locked_users,
        }
