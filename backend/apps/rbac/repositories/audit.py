"""Role version snapshot / audit log persistence."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository

from ..models import RoleAuditLog, RoleVersion


class RoleVersionRepository(BaseRepository[RoleVersion]):
    model = RoleVersion

    def next_version(self, role) -> int:
        latest = self.filter(role=role).order_by("-version").first()
        return (latest.version + 1) if latest is not None else 1

    def snapshots(self, role):
        return self.filter(role=role).order_by("-version")

    def prune(self, role, keep: int) -> int:
        if keep <= 0:
            return 0
        stale = self.filter(role=role).order_by("-version")[keep:]
        deleted = 0
        for version in stale:
            version.delete()
            deleted += 1
        return deleted


class RoleAuditLogRepository(BaseRepository[RoleAuditLog]):
    model = RoleAuditLog

    def record(self, *, role, action: str, actor=None, details: dict | None = None) -> RoleAuditLog:
        return self.create(role=role, action=action, actor=actor, details=details or {})

    def for_role(self, role):
        return self.filter(role=role).select_related("actor").order_by("-created_at")
