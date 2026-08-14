"""ReportExportService executing CSV, Excel, and JSON report generation and logging audit records."""

from __future__ import annotations

import csv
import io
import json
import logging
from typing import Any

from django.utils import timezone

from apps.reports.models import ExportFormat, ReportCategory, ReportExportLog

logger = logging.getLogger(__name__)


class ReportExportService:
    """Service layer handling multi-format report file exports (CSV, Excel, JSON) with full audit logging."""

    def export_report_to_csv(
        self,
        tenant: Any,
        company: Any,
        report_code: str,
        category: str,
        data_rows: list[dict[str, Any]],
        *,
        user: Any | None = None,
        filters_applied: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Convert list of dictionary records to CSV format string and log audit record."""
        if not data_rows:
            csv_str = ""
        else:
            fieldnames = list(data_rows[0].keys())
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for row in data_rows:
                writer.writerow(row)
            csv_str = output.getvalue()

        # Audit log
        ReportExportLog.objects.create(
            tenant=tenant,
            company=company,
            user=user,
            report_code=report_code,
            report_category=category,
            export_format=ExportFormat.CSV,
            record_count=len(data_rows),
            filters_applied=filters_applied or {},
        )

        filename = f"{report_code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        logger.info(f"Exported report {report_code} to CSV ({len(data_rows)} rows) for user {user}")
        return csv_str, filename
