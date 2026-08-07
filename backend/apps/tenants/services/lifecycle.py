"""Tenant lifecycle operations service (activate, suspend, archive, restore, transfer, clone)."""

from __future__ import annotations

import logging

from django.db import transaction

from apps.tenants.exceptions import TenantStatusError
from apps.tenants.models import TenantProfile, TenantSettings
from apps.tenants.repositories import TenantRepository
from apps.tenants.services.provisioning import TenantProvisioningService

logger = logging.getLogger(__name__)


class TenantLifecycleService:
    def __init__(self) -> None:
        self.tenant_repository = TenantRepository()
        self.provisioning_service = TenantProvisioningService()

    @transaction.atomic
    def activate_tenant(self, tenant):
        tenant.activate()
        logger.info("Activated tenant %s", tenant.slug)
        return tenant

    @transaction.atomic
    def suspend_tenant(self, tenant):
        tenant.suspend()
        logger.info("Suspended tenant %s", tenant.slug)
        return tenant

    @transaction.atomic
    def deactivate_tenant(self, tenant):
        tenant.deactivate()
        logger.info("Deactivated tenant %s", tenant.slug)
        return tenant

    @transaction.atomic
    def archive_tenant(self, tenant):
        tenant.archive()
        logger.info("Archived tenant %s", tenant.slug)
        return tenant

    @transaction.atomic
    def restore_tenant(self, tenant):
        tenant.restore()
        logger.info("Restored tenant %s", tenant.slug)
        return tenant

    @transaction.atomic
    def soft_delete_tenant(self, tenant):
        if tenant.is_active and tenant.status == "active":
            raise TenantStatusError("Cannot soft-delete an active tenant. Deactivate or archive it first.")
        self.tenant_repository.delete(tenant)
        logger.info("Soft deleted tenant %s", tenant.slug)
        return tenant

    @transaction.atomic
    def transfer_ownership(self, tenant, new_owner):
        tenant.transfer_ownership(new_owner)
        logger.info("Transferred ownership of tenant %s to user %s", tenant.slug, new_owner.email)
        return tenant

    @transaction.atomic
    def clone_tenant(self, source_tenant, *, new_name: str, new_slug: str, new_code: str | None = None, new_owner=None):
        """Clone template configuration from source_tenant to a new tenant."""
        cloned = self.provisioning_service.provision_tenant(
            name=new_name,
            slug=new_slug,
            code=new_code,
            owner_id=new_owner.pk if new_owner else None,
            plan=source_tenant.subscription_tier,
        )

        # Clone profile settings
        source_profile = getattr(source_tenant, "profile", None)
        if source_profile and getattr(cloned, "profile", None):
            cloned.profile.business_type = source_profile.business_type
            cloned.profile.country = source_profile.country
            cloned.profile.currency = source_profile.currency
            cloned.profile.timezone = source_profile.timezone
            cloned.profile.date_format = source_profile.date_format
            cloned.profile.time_format = source_profile.time_format
            cloned.profile.save()

        # Clone settings
        source_settings = getattr(source_tenant, "settings", None)
        if source_settings and getattr(cloned, "settings", None):
            cloned.settings.tax_configuration = source_settings.tax_configuration
            cloned.settings.business_hours = source_settings.business_hours
            cloned.settings.feature_flags = source_settings.feature_flags
            cloned.settings.password_policy = source_settings.password_policy
            cloned.settings.theme = source_settings.theme
            cloned.settings.save()

        logger.info("Cloned tenant %s to new tenant %s", source_tenant.slug, cloned.slug)
        return cloned
