"""Role hierarchy persistence."""

from __future__ import annotations

from collections import deque

from apps.common.repositories.base import BaseRepository

from ..models import RoleHierarchy


class RoleHierarchyRepository(BaseRepository[RoleHierarchy]):
    model = RoleHierarchy

    def link(self, child_role_id, parent_role_id) -> RoleHierarchy:
        link, _ = self.get_or_create(child_role_id=child_role_id, parent_role_id=parent_role_id)
        return link

    def unlink(self, child_role_id, parent_role_id) -> bool:
        deleted, _ = self.filter(child_role_id=child_role_id, parent_role_id=parent_role_id).delete()
        return deleted > 0

    def ancestors(self, role_id) -> set:
        """All role ids the given role (directly or transitively) inherits from."""
        ancestors: set = set()
        frontier = {role_id}
        while frontier:
            parents = set(self.filter(child_role_id__in=frontier).values_list("parent_role_id", flat=True))
            new = parents - ancestors
            ancestors |= new
            frontier = new
        ancestors.discard(role_id)
        return ancestors

    def descendants(self, role_id) -> set:
        """All role ids that (directly or transitively) inherit from the given role."""
        descendants: set = set()
        frontier = {role_id}
        while frontier:
            children = set(self.filter(parent_role_id__in=frontier).values_list("child_role_id", flat=True))
            new = children - descendants
            descendants |= new
            frontier = new
        descendants.discard(role_id)
        return descendants

    def has_cycle(self, child_role_id, parent_role_id) -> bool:
        """Whether adding ``child → parent`` would close an inheritance cycle."""
        if child_role_id == parent_role_id:
            return True
        return child_role_id in self.ancestors(parent_role_id)
