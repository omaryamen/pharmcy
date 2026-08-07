"""Tenant Domain Service for managing host resolution, custom domains, and SSL verification."""

from __future__ import annotations

import logging

from django.db import transaction

from apps.tenants.exceptions import DomainVerificationError, DuplicateSlugError
from apps.tenants.models import DomainType, SSLStatus, TenantDomain
from apps.tenants.repositories import TenantDomainRepository

logger = logging.getLogger(__name__)


class TenantDomainService:
    def __init__(self) -> None:
        self.domain_repository = TenantDomainRepository()

    @transaction.atomic
    def add_domain(self, tenant, *, domain_name: str, domain_type: str = DomainType.CUSTOM, is_primary: bool = False):
        clean_name = domain_name.lower().strip()
        if self.domain_repository.exists(domain_name=clean_name):
            raise DuplicateSlugError(f"Domain name '{clean_name}' is already registered.", field="domain_name")

        domain = self.domain_repository.create(
            tenant=tenant,
            domain_name=clean_name,
            domain_type=domain_type,
            is_verified=(domain_type == DomainType.SUBDOMAIN),
            ssl_status=SSLStatus.ACTIVE if domain_type == DomainType.SUBDOMAIN else SSLStatus.PENDING,
            is_primary=is_primary,
        )
        logger.info("Added domain %s for tenant %s", clean_name, tenant.slug)
        return domain

    @transaction.atomic
    def verify_domain(self, tenant, domain_id: str):
        domain = self.domain_repository.get_or_none(pk=domain_id, tenant=tenant)
        if not domain:
            raise DomainVerificationError("Domain not found for this tenant.")

        # Simulate verification check
        domain.is_verified = True
        domain.ssl_status = SSLStatus.ACTIVE
        domain.save(update_fields=["is_verified", "ssl_status", "updated_at"])
        logger.info("Verified custom domain %s for tenant %s", domain.domain_name, tenant.slug)
        return domain

    @transaction.atomic
    def set_primary_domain(self, tenant, domain_id: str):
        domain = self.domain_repository.get_or_none(pk=domain_id, tenant=tenant)
        if not domain or not domain.is_verified:
            raise DomainVerificationError("Domain must be verified before setting as primary.")

        TenantDomain.objects.filter(tenant=tenant).update(is_primary=False)
        domain.is_primary = True
        domain.save(update_fields=["is_primary", "updated_at"])
        return domain

    @transaction.atomic
    def remove_domain(self, tenant, domain_id: str):
        domain = self.domain_repository.get_or_none(pk=domain_id, tenant=tenant)
        if not domain:
            return None
        if domain.is_primary:
            raise DomainVerificationError("Cannot remove the primary domain of a tenant.")
        self.domain_repository.delete(domain)
        return domain
