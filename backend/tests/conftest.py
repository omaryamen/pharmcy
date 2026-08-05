"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from tests.factories import TenantFactory, UserFactory


@pytest.fixture(scope="session", autouse=True)
def _prepare_static_root():
    """Whitenoise warns (raised as error) when STATIC_ROOT is missing."""
    from pathlib import Path

    from django.conf import settings

    Path(settings.STATIC_ROOT).mkdir(parents=True, exist_ok=True)


@pytest.fixture(autouse=True)
def _use_tmp_media_root(tmp_path):
    """Keep test media files out of the real media directory."""
    from django.conf import settings

    settings.MEDIA_ROOT = str(tmp_path / "media")


@pytest.fixture(autouse=True)
def _clear_mail_outbox():
    """Each test starts with an empty locmem email outbox."""
    from django.core import mail

    mail.outbox = []


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def superuser(db):
    from tests.factories import SuperUserFactory

    return SuperUserFactory()


@pytest.fixture
def tenant(db):
    return TenantFactory()


@pytest.fixture
def api_client():
    """Anonymous API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(db, user):
    """API client authenticated with a JWT access token."""
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def tenant_authenticated_client(db, user, tenant):
    """API client authenticated and carrying a tenant header."""
    from rest_framework_simplejwt.tokens import RefreshToken

    user.tenants.add(tenant)
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        HTTP_X_TENANT_ID=str(tenant.pk),
    )
    return client
