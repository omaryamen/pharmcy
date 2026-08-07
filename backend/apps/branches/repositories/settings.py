"""Branch Settings repository."""

from __future__ import annotations

from apps.branches.models import BranchSettings
from apps.common.repositories.base import BaseRepository


class BranchSettingsRepository(BaseRepository[BranchSettings]):
    model = BranchSettings

    def get_for_branch(self, branch) -> BranchSettings | None:
        return self.get_or_none(branch=branch)
