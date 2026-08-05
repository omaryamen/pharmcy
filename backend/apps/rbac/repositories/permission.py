"""Permission catalog persistence."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository

from ..models import Permission


class PermissionRepository(BaseRepository[Permission]):
    model = Permission

    def active(self):
        return self.filter(is_active=True)

    def get_by_code(self, code: str) -> Permission | None:
        return self.get_or_none(code=code)

    def codes(self) -> list[str]:
        return list(self.filter(is_active=True).values_list("code", flat=True))
