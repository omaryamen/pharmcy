"""User repository extending base data access."""

from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.common.repositories.base import BaseRepository

User = get_user_model()


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.get_or_none(email=email.lower().strip())

    def get_by_username(self, username: str) -> User | None:
        return self.get_or_none(username=username.strip())

    def for_tenant(self, tenant) -> list[User]:
        return list(self.filter(tenants=tenant))
