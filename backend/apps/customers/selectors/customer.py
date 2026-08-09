"""Customer selector functions for tenant, company & branch-scoped queries."""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet

from apps.customers.models import Customer
from apps.customers.repositories import CustomerRepository


class CustomerSelector:
    def __init__(self) -> None:
        self.repository = CustomerRepository()

    def list_customers(
        self,
        tenant,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        customer_type: str | None = None,
        status: str | None = None,
        customer_group: str | None = None,
        credit_allowed: bool | None = None,
        search: str | None = None,
    ) -> QuerySet[Customer]:
        qs = self.repository.filter(tenant=tenant).select_related("company", "preferred_branch", "tenant")

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(preferred_branch_id=branch_id)
        if customer_type:
            qs = qs.filter(customer_type=customer_type)
        if status:
            qs = qs.filter(status=status)
        if customer_group:
            qs = qs.filter(customer_group=customer_group)
        if credit_allowed is not None:
            qs = qs.filter(credit_allowed=credit_allowed)

        if search:
            qs = qs.filter(
                Q(code__icontains=search)
                | Q(customer_number__icontains=search)
                | Q(arabic_name__icontains=search)
                | Q(english_name__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone__icontains=search)
                | Q(mobile__icontains=search)
                | Q(email__icontains=search)
                | Q(national_id__icontains=search)
                | Q(passport_number__icontains=search)
                | Q(insurance_member_number__icontains=search)
                | Q(membership_number__icontains=search)
                | Q(loyalty_account_number__icontains=search)
            )

        return qs

    def get_customer_detail(self, tenant, customer_id: str) -> Customer | None:
        return (
            self.repository.filter(tenant=tenant, pk=customer_id)
            .select_related("company", "preferred_branch", "tenant", "medical_profile")
            .prefetch_related("addresses")
            .first()
        )

    def search_customers(self, tenant, query: str, limit: int = 20) -> QuerySet[Customer]:
        """Fast lookup endpoint specifically tailored for POS and sales lookup."""
        query_clean = query.strip()
        if not query_clean:
            return self.repository.model.objects.none()

        return (
            self.repository.filter(tenant=tenant, status="active")
            .filter(
                Q(code__icontains=query_clean)
                | Q(customer_number__icontains=query_clean)
                | Q(arabic_name__icontains=query_clean)
                | Q(english_name__icontains=query_clean)
                | Q(phone__icontains=query_clean)
                | Q(mobile__icontains=query_clean)
                | Q(email__icontains=query_clean)
                | Q(national_id__icontains=query_clean)
                | Q(insurance_member_number__icontains=query_clean)
                | Q(membership_number__icontains=query_clean)
            )
            .select_related("company", "preferred_branch")[:limit]
        )

    def get_customer_stats(self, tenant) -> dict[str, Any]:
        qs = self.repository.filter(tenant=tenant)
        total_customers = qs.count()
        active_customers = qs.filter(status="active").count()
        blocked_customers = qs.filter(status="blocked").count()
        suspended_customers = qs.filter(status="suspended").count()
        individual_customers = qs.filter(customer_type="individual").count()
        organization_customers = qs.filter(customer_type="organization").count()
        credit_allowed_customers = qs.filter(credit_allowed=True).count()

        return {
            "tenant_id": str(tenant.pk),
            "total_customers": total_customers,
            "active_customers": active_customers,
            "blocked_customers": blocked_customers,
            "suspended_customers": suspended_customers,
            "individual_customers": individual_customers,
            "organization_customers": organization_customers,
            "credit_allowed_customers": credit_allowed_customers,
        }
