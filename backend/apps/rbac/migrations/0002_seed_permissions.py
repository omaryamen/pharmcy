"""Seed the permission catalog from the code constants (versioned snapshot)."""

from __future__ import annotations

from django.db import migrations
from apps.rbac.constants import PERMISSION_CATALOG

PERMISSION_SEED = [
    {**entry, "is_system": True, "is_active": True}
    for entry in PERMISSION_CATALOG
]


def seed_permissions(apps, schema_editor):
    Permission = apps.get_model("rbac", "Permission")
    existing_codes = set(Permission.objects.values_list("code", flat=True))
    catalog_codes = {entry["code"] for entry in PERMISSION_SEED}

    # Remove permissions no longer in catalog
    Permission.objects.exclude(code__in=catalog_codes).delete()

    to_create = [entry for entry in PERMISSION_SEED if entry["code"] not in existing_codes]
    if to_create:
        Permission.objects.bulk_create(
            [Permission(**entry) for entry in to_create],
            batch_size=500,
        )


def unseed_permissions(apps, schema_editor):
    Permission = apps.get_model("rbac", "Permission")
    codes = [entry["code"] for entry in PERMISSION_SEED]
    Permission.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rbac", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_permissions, reverse_code=unseed_permissions),
    ]
