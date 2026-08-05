"""Effective-permission resolver.

The resolver turns a role's own links *and* everything it inherits from its
parents into a single ``code → (allow, source)`` map. Within one role direct
links always override inherited ones — a direct deny beats an inherited
grant, and a direct grant beats an inherited deny.
"""

from __future__ import annotations

from ..models import RoleHierarchy, RolePermission


class PermissionResolver:
    """Computes role permission maps and inheritance closures."""

    def ancestors(self, role) -> set:
        """Every role id ``role`` inherits from, transitively (excluding self)."""
        ancestor_ids: set = set()
        frontier = {role.pk}
        while frontier:
            parents = set(
                RoleHierarchy.objects.filter(child_role_id__in=frontier).values_list("parent_role_id", flat=True)
            )
            new = parents - ancestor_ids
            ancestor_ids |= new
            frontier = new
        ancestor_ids.discard(role.pk)
        return ancestor_ids

    def role_permission_map(self, role) -> dict:
        """Return ``{code: (allow, source)}`` for a role.

        ``source`` is ``"direct"`` for links set on the role itself and
        ``"inherited"`` for anything coming from a parent. Direct wins over
        inherited; the order of two links from different parents is
        irrelevant because both are ``"inherited"``.
        """
        ancestor_ids = self.ancestors(role)
        all_ids = {role.pk} | ancestor_ids
        links = RolePermission.objects.filter(role_id__in=all_ids, permission__is_active=True).select_related(
            "permission"
        )
        result: dict = {}
        for link in links:
            code = link.permission.code
            source = "direct" if link.role_id == role.pk else "inherited"
            current = result.get(code)
            if current is None or (current[1] == "inherited" and source == "direct"):
                result[code] = (link.allow, source)
        return result
