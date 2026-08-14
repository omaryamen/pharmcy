"""TemplateEngineService rendering template text placeholders without arbitrary code execution."""

from __future__ import annotations

import logging
import re
from typing import Any

from apps.notifications.exceptions import TemplateRenderingError
from apps.notifications.models import NotificationTemplate

logger = logging.getLogger(__name__)


class TemplateEngineService:
    """Service layer executing safe dictionary-based variable placeholder substitution in templates."""

    VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

    def render_template(
        self,
        template: NotificationTemplate,
        context: dict[str, Any],
    ) -> tuple[str, str]:
        """Render subject_template and body_template by replacing {{var}} placeholders safely."""
        subject = self._substitute_placeholders(template.subject_template, context)
        body = self._substitute_placeholders(template.body_template, context)
        return subject, body

    def _substitute_placeholders(self, text: str, context: dict[str, Any]) -> str:
        def replace_match(match: re.Match) -> str:
            var_name = match.group(1)
            val = context.get(var_name, "")
            return str(val)

        return self.VARIABLE_PATTERN.sub(replace_match, text)
