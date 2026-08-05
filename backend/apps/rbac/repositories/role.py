"""Role / role-permission persistence."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository

from ..models import Permission, Role, RolePermission


class RoleRepository(BaseRepository[Role]):
    model = Role

    def get_by_code(self, tenant, code: str) -> Role | None:
        return self.get_or_none(tenant=tenant, code=code)

    def active(self):
        return self.filter(is_active=True)


class RolePermissionRepository(BaseRepository[RolePermission]):
    model = RolePermission

    def for_role(self, role) -> list[RolePermission]:
        return list(self.filter(role=role).select_related("permission"))

    def replace_for_role(self, role, permission_map: dict[str, bool]) -> None:
        """Replace every link of ``role`` with the given code→allow mapping.

        Codes not present in ``permission_map`` are removed; unknown codes
        raise ``Permission.DoesNotExist`` and abort the transaction.
        """
        codes = list(permission_map.keys())
        permissions = {p.code: p for p in Permission.objects.filter(code__in=codes)}
        unknown = set(codes) - set(permissions)
        if unknown:
            missing = ", ".join(sorted(unknown))
            raise Permission.DoesNotExist(f"Unknown permission codes: {missing}")

        existing = {link.permission.code: link for link in self.for_role(role)}
        desired = set(codes)

        for code, link in existing.items():
            if code not in desired:
                link.delete()

        for code, allow in permission_map.items():
            link = existing.get(code)
            if link is None:
                self.create(role=role, permission=permissions[code], allow=allow)
            elif link.allow != allow:
                self.update(link, allow=allow)
