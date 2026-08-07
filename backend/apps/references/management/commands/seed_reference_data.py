"""Django Management Command to seed pharmaceutical reference data."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.core.models import Tenant
from apps.references.services import ReferenceDataService


class Command(BaseCommand):
    help = "Seed standard pharmaceutical reference data across all active tenants."

    def add_arguments(self, parser):
        parser.add_argument("--tenant-id", type=str, help="Specific tenant UUID to seed")

    def handle(self, *args, **options):
        tenant_id = options.get("tenant_id")
        service = ReferenceDataService()

        if tenant_id:
            tenants = Tenant.objects.filter(pk=tenant_id)
        else:
            tenants = Tenant.objects.all()

        total_seeded = 0
        for tenant in tenants:
            result = service.seed_system_defaults(tenant)
            self.stdout.write(self.style.SUCCESS(f"Seeded tenant '{tenant.slug}': {result}"))
            total_seeded += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded reference data for {total_seeded} tenants."))
