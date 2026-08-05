"""Custom user model for PharmaCloud ERP.

Identity core: email-based login, UUID primary key, an explicit lifecycle
``status``, soft delete and audit stamps. JWT authentication uses this model
via ``AUTH_USER_MODEL = "core.User"``.

``status`` is the source of truth for the account lifecycle; ``is_active``
is derived from it in ``save()`` so Django's auth checks stay in sync.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import AuditBase, SoftDeleteBase, TimeStampedBase, UUIDBase
from apps.common.models.managers import AllObjectsManager


class UserStatus(models.TextChoices):
    """Lifecycle states a user account can be in."""

    PENDING_VERIFICATION = "pending_verification", _("Pending verification")
    ACTIVE = "active", _("Active")
    LOCKED = "locked", _("Locked")
    INACTIVE = "inactive", _("Inactive")


class UserManager(BaseUserManager):
    """Manager for the custom User model.

    The default queryset hides soft-deleted accounts so they can neither
    authenticate nor be selected by normal queries. Use ``User.all_objects``
    to inspect deleted accounts.
    """

    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def _create_user(
        self,
        email: str,
        first_name: str,
        password: str | None,
        last_name: str = "",
        **extra_fields,
    ):
        if not email:
            raise ValueError("Users must provide an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        first_name: str,
        password: str | None = None,
        last_name: str = "",
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("status", UserStatus.ACTIVE)
        return self._create_user(email, first_name, password, last_name, **extra_fields)

    def create_superuser(
        self,
        email: str,
        first_name: str,
        password: str | None = None,
        last_name: str = "",
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatus.ACTIVE)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, first_name, password, last_name, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, UUIDBase, TimeStampedBase, SoftDeleteBase, AuditBase):
    """Platform user. Belongs to zero or more tenants (via ``tenants`` M2M).

    An account transitions between ``UserStatus`` states; ``is_active`` is
    always kept consistent with ``status`` and ``is_deleted``.
    """

    # --- Identity -------------------------------------------------------
    email = models.EmailField(unique=True, db_index=True, verbose_name="Email")
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Username",
    )
    first_name = models.CharField(max_length=150, blank=True, verbose_name="First name")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Last name")
    phone = models.CharField(max_length=32, blank=True, default="", verbose_name="Phone")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Avatar")

    # --- Preferences ----------------------------------------------------
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default="en",
        verbose_name="Language",
    )
    timezone = models.CharField(max_length=64, default="UTC", verbose_name="Timezone")

    # --- Lifecycle ------------------------------------------------------
    status = models.CharField(
        max_length=24,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        db_index=True,
        verbose_name="Status",
    )
    email_verified = models.BooleanField(default=False, verbose_name="Email verified")
    phone_verified = models.BooleanField(default=False, verbose_name="Phone verified")

    # --- Django auth flags ----------------------------------------------
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Active")
    is_staff = models.BooleanField(default=False, verbose_name="Staff")

    # --- Security -------------------------------------------------------
    failed_login_attempts = models.PositiveSmallIntegerField(default=0, verbose_name="Failed login attempts")
    password_changed_at = models.DateTimeField(null=True, blank=True, verbose_name="Password changed at")

    # --- Multi-tenancy --------------------------------------------------
    tenants = models.ManyToManyField(
        "core.Tenant",
        blank=True,
        related_name="users",
        verbose_name="Tenants",
    )

    objects = UserManager()
    all_objects = AllObjectsManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]
    EMAIL_FIELD = "email"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    # ------------------------------------------------------------------
    # Identity helpers
    # ------------------------------------------------------------------
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.first_name or self.email

    def __str__(self) -> str:
        return self.email

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs) -> None:
        if self.is_deleted:
            self.is_active = False
        else:
            self.is_active = self.status == UserStatus.ACTIVE
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents: bool = False) -> None:
        """Soft-delete the account and immediately disable authentication."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["is_deleted", "deleted_at", "is_active", "updated_at"])

    def set_password(self, raw_password: str) -> None:
        super().set_password(raw_password)
        self.password_changed_at = timezone.now()

    # ------------------------------------------------------------------
    # Lifecycle transitions (state is persisted; services own the policy)
    # ------------------------------------------------------------------
    @property
    def is_locked(self) -> bool:
        return self.status == UserStatus.LOCKED

    @property
    def is_deactivated(self) -> bool:
        return self.status == UserStatus.INACTIVE

    @property
    def is_pending_verification(self) -> bool:
        return self.status == UserStatus.PENDING_VERIFICATION

    def lock_account(self) -> None:
        self.status = UserStatus.LOCKED
        self.save(update_fields=["status", "is_active", "updated_at"])

    def unlock_account(self) -> None:
        self.failed_login_attempts = 0
        self.status = UserStatus.ACTIVE
        self.save(update_fields=["status", "failed_login_attempts", "is_active", "updated_at"])

    def deactivate(self) -> None:
        self.status = UserStatus.INACTIVE
        self.save(update_fields=["status", "is_active", "updated_at"])

    def activate(self) -> None:
        self.status = UserStatus.ACTIVE
        self.save(update_fields=["status", "is_active", "updated_at"])

    def register_failed_login(self, max_attempts: int) -> bool:
        """Record one failed login; locks the account at the threshold.

        Returns ``True`` when the account was locked by this attempt.
        """
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.lock_account()
            return True
        self.save(update_fields=["failed_login_attempts", "updated_at"])
        return False

    def reset_failed_logins(self) -> None:
        if self.failed_login_attempts != 0:
            self.failed_login_attempts = 0
            self.save(update_fields=["failed_login_attempts", "updated_at"])
