"""Company service for business logic and lifecycle management."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils.text import slugify

from apps.companies.exceptions import CompanyDeleteForbiddenError, DuplicateCompanyNameError
from apps.companies.models import Company, CompanySettings, CompanyStatus
from apps.companies.repositories import CompanyRepository, CompanySettingsRepository

logger = logging.getLogger(__name__)


class CompanyService:
    def __init__(self) -> None:
        self.repository = CompanyRepository()
        self.settings_repository = CompanySettingsRepository()

    @transaction.atomic
    def create_company(
        self,
        tenant,
        *,
        legal_name: str,
        code: str | None = None,
        slug: str | None = None,
        commercial_name: str = "",
        business_type: str = "retail_pharmacy",
        country: str = "Yemen",
        currency: str = "YER",
        timezone_str: str = "UTC",
        **extra_fields,
    ) -> Company:
        clean_slug = slugify(slug or legal_name)
        clean_code = (code or clean_slug).lower().replace("-", "_")

        if self.repository.exists(tenant=tenant, legal_name=legal_name):
            raise DuplicateCompanyNameError(f"A company named '{legal_name}' already exists in this tenant.", field="legal_name")
        if self.repository.exists(tenant=tenant, code=clean_code):
            raise DuplicateCompanyNameError(f"A company with code '{clean_code}' already exists in this tenant.", field="code")
        if self.repository.exists(tenant=tenant, slug=clean_slug):
            raise DuplicateSlugError(f"A company with slug '{clean_slug}' already exists in this tenant.", field="slug")

        company = self.repository.create(
            tenant=tenant,
            legal_name=legal_name,
            commercial_name=commercial_name or legal_name,
            code=clean_code,
            slug=clean_slug,
            business_type=business_type,
            country=country,
            currency=currency,
            timezone=timezone_str,
            status=CompanyStatus.ACTIVE,
            **extra_fields,
        )

        # Create default company settings
        self.settings_repository.create(
            company=company,
            tenant=tenant,
            default_currency=currency,
        )

        logger.info("Created company %s (%s) for tenant %s", company.legal_name, company.code, tenant.slug)
        return company

    @transaction.atomic
    def update_company(self, company: Company, **fields) -> Company:
        return self.repository.update(company, **fields)

    @transaction.atomic
    def activate_company(self, company: Company) -> Company:
        company.activate()
        logger.info("Activated company %s", company.code)
        return company

    @transaction.atomic
    def deactivate_company(self, company: Company) -> Company:
        company.deactivate()
        logger.info("Deactivated company %s", company.code)
        return company

    @transaction.atomic
    def suspend_company(self, company: Company) -> Company:
        company.suspend()
        logger.info("Suspended company %s", company.code)
        return company

    @transaction.atomic
    def archive_company(self, company: Company) -> Company:
        company.archive()
        logger.info("Archived company %s", company.code)
        return company

    @transaction.atomic
    def restore_company(self, company: Company) -> Company:
        company.restore()
        logger.info("Restored company %s", company.code)
        return company

    @transaction.atomic
    def soft_delete_company(self, company: Company) -> Company:
        # Check active dependencies guard
        has_branches = getattr(company, "branches", None) and company.branches.filter(is_deleted=False).exists()
        has_warehouses = getattr(company, "warehouses", None) and company.warehouses.filter(is_deleted=False).exists()
        if has_branches or has_warehouses:
            raise CompanyDeleteForbiddenError("Cannot delete company with active branches or warehouses.")

        self.repository.delete(company)
        logger.info("Soft deleted company %s", company.code)
        return company

    @transaction.atomic
    def clone_company(self, source_company: Company, *, new_legal_name: str, new_code: str, new_slug: str) -> Company:
        cloned = self.create_company(
            tenant=source_company.tenant,
            legal_name=new_legal_name,
            code=new_code,
            slug=new_slug,
            commercial_name=source_company.commercial_name,
            business_type=source_company.business_type,
            country=source_company.country,
            city=source_company.city,
            currency=source_company.currency,
            timezone_str=source_company.timezone,
        )

        source_settings = getattr(source_company, "settings", None)
        if source_settings and getattr(cloned, "settings", None):
            cloned.settings.tax_configuration = source_settings.tax_configuration
            cloned.settings.pos_settings = source_settings.pos_settings
            cloned.settings.inventory_settings = source_settings.inventory_settings
            cloned.settings.document_prefixes = source_settings.document_prefixes
            cloned.settings.save()

        return cloned
