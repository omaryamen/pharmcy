"""Multi-tenancy model support: tenant-scoped abstract base."""

from __future__ import annotations

from django.db import models

from .managers import TenantManager


class TenantAwareModel(models.Model):
    """Abstract base for models whose rows belong to exactly one tenant.

    The tenant FK is a shared, indexed column — data isolation is enforced
    at the query layer (repository/service/viewset) and by the
    ``HasTenantContext`` / ``IsTenantMember`` permissions.
    """

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
        verbose_name="Tenant",
    )

    objects = TenantManager()

    class Meta:
        abstract = True
