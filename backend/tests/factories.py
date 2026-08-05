"""Factory classes for the test suite (factory_boy)."""

from __future__ import annotations

import factory
from faker import Faker

from apps.core.models import Tenant, User, UserStatus
from apps.core.models.tenant import TenantStatus
from apps.rbac.models import Permission, PermissionScope, Role, RoleGroup

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


class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission
        django_get_or_create = ("code",)

    code = factory.Sequence(lambda n: f"factory.module{n}.read")
    name = factory.LazyAttribute(lambda o: o.code.replace(".", " ").title())
    module = factory.Sequence(lambda n: f"factory_module{n}")
    category = "general"
    action = "read"
    scope = PermissionScope.TENANT
    is_system = False
    is_active = True


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    tenant = factory.SubFactory(TenantFactory)
    name = factory.Sequence(lambda n: f"Role {n}")
    code = factory.Sequence(lambda n: f"role_{n}")
    description = ""
    is_protected = False
    is_default = False
    is_active = True


class RoleGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RoleGroup

    tenant = factory.SubFactory(TenantFactory)
    name = factory.Sequence(lambda n: f"Group {n}")
    code = factory.Sequence(lambda n: f"group_{n}")
    description = ""
    is_active = True
