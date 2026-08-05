"""Factory classes for the test suite (factory_boy)."""

from __future__ import annotations

import factory
from faker import Faker

from apps.core.models import Tenant, User, UserStatus
from apps.core.models.tenant import TenantStatus

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@pharmacloud.test")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = factory.Faker("phone_number")
    language = "en"
    timezone = "UTC"
    status = UserStatus.ACTIVE
    email_verified = True
    phone_verified = False
    is_active = True
    is_staff = False
    is_superuser = False

    # Hash the password instead of storing it in plain text.
    password = factory.PostGenerationMethodCall("set_password", "TestPass!123")

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        if create:
            instance.save()


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant

    name = factory.Sequence(lambda n: f"Tenant {n}")
    code = factory.Sequence(lambda n: f"TEN{n:04d}")
    slug = factory.Sequence(lambda n: f"tenant-{n}")
    status = TenantStatus.ACTIVE
    timezone = "UTC"
    locale = "en"
    subscription_tier = "trial"
    is_active = True
