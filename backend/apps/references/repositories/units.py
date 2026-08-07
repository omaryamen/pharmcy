"""Strength Units, UOMs, and Package Types Repositories."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.references.models import PackageType, StrengthUnit, UnitOfMeasure


class StrengthUnitRepository(BaseRepository[StrengthUnit]):
    model = StrengthUnit


class UnitOfMeasureRepository(BaseRepository[UnitOfMeasure]):
    model = UnitOfMeasure


class PackageTypeRepository(BaseRepository[PackageType]):
    model = PackageType
