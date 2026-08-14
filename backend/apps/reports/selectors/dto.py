"""ReportFilterDTO dataclass for standardizing report parameters across selectors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from django.utils import timezone
from dateutil.relativedelta import relativedelta

from apps.reports.models import PeriodType


@dataclass
class ReportFilterDTO:
    tenant: Any
    company_id: str | None = None
    branch_id: str | None = None
    warehouse_id: str | None = None
    category_id: str | None = None
    supplier_id: str | None = None
    customer_id: str | None = None
    user_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    period_type: str | None = None
    currency: str = "USD"

    def resolve_dates(self) -> tuple[date, date]:
        """Resolve period_type or return start_date and end_date defaulting to current month."""
        today = timezone.now().date()
        if self.start_date and self.end_date:
            return self.start_date, self.end_date

        pt = self.period_type or PeriodType.THIS_MONTH

        if pt == PeriodType.TODAY:
            return today, today
        elif pt == PeriodType.YESTERDAY:
            y = today - relativedelta(days=1)
            return y, y
        elif pt == PeriodType.THIS_WEEK:
            start = today - relativedelta(days=today.weekday())
            return start, today
        elif pt == PeriodType.LAST_WEEK:
            end = today - relativedelta(days=today.weekday() + 1)
            start = end - relativedelta(days=6)
            return start, end
        elif pt == PeriodType.THIS_MONTH:
            start = today.replace(day=1)
            return start, today
        elif pt == PeriodType.LAST_MONTH:
            first_this_month = today.replace(day=1)
            end = first_this_month - relativedelta(days=1)
            start = end.replace(day=1)
            return start, end
        elif pt == PeriodType.THIS_YEAR:
            start = today.replace(month=1, day=1)
            return start, today
        elif pt == PeriodType.LAST_YEAR:
            start = today.replace(year=today.year - 1, month=1, day=1)
            end = today.replace(year=today.year - 1, month=12, day=31)
            return start, end

        start = today.replace(day=1)
        return start, today
