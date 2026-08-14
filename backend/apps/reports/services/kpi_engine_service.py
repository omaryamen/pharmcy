"""KpiEngineService calculating derived KPI metrics, period-over-period comparisons, and growth percentages."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)


class KpiEngineService:
    """Service layer computing derived KPI comparisons, variance deltas, and growth percentages."""

    def calculate_kpi_metric(
        self,
        name: str,
        current_value: Decimal | float | int,
        previous_value: Decimal | float | int,
        *,
        unit: str = "USD",
    ) -> dict[str, Any]:
        """Compute current value, previous value, absolute change, and growth percentage safely."""
        curr = Decimal(str(current_value))
        prev = Decimal(str(previous_value))

        diff = curr - prev

        if prev == Decimal("0.0000"):
            pct_change = Decimal("100.0000") if curr > Decimal("0.0000") else Decimal("0.0000")
        else:
            pct_change = (diff / abs(prev)) * Decimal("100.0000")

        trend = "up" if diff > Decimal("0.0000") else ("down" if diff < Decimal("0.0000") else "flat")

        return {
            "kpi_name": name,
            "current_value": curr,
            "previous_value": prev,
            "difference": diff,
            "percentage_change": round(pct_change, 2),
            "trend": trend,
            "unit": unit,
        }
