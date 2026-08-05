"""Core model tests: User and Tenant."""

from __future__ import annotations

import pytest
from django.db import IntegrityError

from apps.core.models import Tenant, User, UserStatus
from apps.core.models.tenant import TenantStatus


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_hashes_password(self):
        user = User.objects.create_user(email="pharmacist@pharmacloud.test", first_name="Ahmed", password="Secret!123")

        assert user.check_password("Secret!123") is True
        assert user.has_usable_password() is True
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.email_verified is False
        assert user.password_changed_at is not None

    def test_create_user_stores_names(self):
        user = User.objects.create_user(
            email="pharmacist@pharmacloud.test",
            first_name="Ahmed",
            last_name="Ali",
            password="Secret!123",
        )
        assert user.first_name == "Ahmed"
        assert user.last_name == "Ali"
        assert user.full_name == "Ahmed Ali"

    def test_email_is_normalized(self):
        user = User.objects.create_user(email="UPPER@Pharmacloud.TEST", first_name="Upper", password="Secret!123")
        assert user.email == "UPPER@pharmacloud.test"

    def test_email_is_unique(self, user):
        with pytest.raises(IntegrityError):
            User.objects.create_user(email=user.email, first_name="Duplicate", password="Secret!123")

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="admin@pharmacloud.test", first_name="Admin", password="Secret!123"
        )
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.email_verified is True

    def test_superuser_requires_staff_flag(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="bad@pharmacloud.test",
                first_name="Bad",
                password="Secret!123",
                is_staff=False,
            )

    def test_str(self, user):
        assert str(user) == user.email

    def test_soft_delete_excludes_from_default_manager(self, user):
        user.delete()
        assert User.objects.filter(pk=user.pk).exists() is False
        assert User.all_objects.filter(pk=user.pk).exists() is True

    def test_soft_deleted_user_cannot_authenticate(self, user):
        user.delete()
        assert user.is_active is False
        assert user.is_deleted is True

    def test_status_drives_is_active(self, user):
        user.deactivate()
        assert user.status == UserStatus.INACTIVE
        assert user.is_active is False

        user.activate()
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True

    def test_lock_and_unlock(self, user):
        user.lock_account()
        assert user.status == UserStatus.LOCKED
        assert user.is_active is False
        assert user.is_locked is True

        user.unlock_account()
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True
        assert user.failed_login_attempts == 0

    def test_register_failed_login_locks_at_threshold(self, user):
        assert user.register_failed_login(max_attempts=5) is False
        assert user.failed_login_attempts == 1

        for _ in range(3):
            user.register_failed_login(max_attempts=5)
        assert user.failed_login_attempts == 4
        assert user.status == UserStatus.ACTIVE

        assert user.register_failed_login(max_attempts=5) is True
        assert user.status == UserStatus.LOCKED
        assert user.is_active is False

    def test_reset_failed_logins(self, user):
        user.register_failed_login(max_attempts=5)
        user.reset_failed_logins()
        assert user.failed_login_attempts == 0

    def test_audit_fields_populated_by_request_context(self, user):
        assert hasattr(user, "created_by")
        assert hasattr(user, "updated_by")
        assert user.created_by is None


@pytest.mark.django_db
class TestTenantModel:
    def test_default_status_is_trial(self):
        tenant = Tenant.objects.create(name="Al-Shifa Pharmacy", code="ASH1", slug="al-shifa")
        assert tenant.status == TenantStatus.TRIAL

    def test_activate(self, tenant):
        tenant.deactivate()
        tenant.activate()
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.is_active is True

    def test_suspend(self, tenant):
        tenant.suspend()
        assert tenant.status == TenantStatus.SUSPENDED
        assert tenant.is_active is False

    def test_tenant_slug_is_unique(self, tenant):
        with pytest.raises(IntegrityError):
            Tenant.objects.create(name="Duplicate", code="DUP1", slug=tenant.slug)

    def test_str(self, tenant):
        assert str(tenant) == tenant.name
