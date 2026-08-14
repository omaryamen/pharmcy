"""RuleEngineService evaluating event rules, condition JSON, recipient resolution, and alert deduplication."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.notifications.models import (
    DomainEvent,
    Notification,
    NotificationPreference,
    NotificationPriority,
    NotificationRule,
    NotificationStatus,
)
from apps.notifications.services.number_generator import NotificationNumberGenerator
from apps.notifications.services.template_engine_service import TemplateEngineService

User = get_user_model()
logger = logging.getLogger(__name__)


class RuleEngineService:
    """Service layer evaluating active NotificationRules for DomainEvents and generating Notifications."""

    def __init__(
        self,
        template_engine: TemplateEngineService | None = None,
        number_generator: NotificationNumberGenerator | None = None,
    ) -> None:
        self.template_engine = template_engine or TemplateEngineService()
        self.number_generator = number_generator or NotificationNumberGenerator()

    def evaluate_event_rules(self, event: DomainEvent) -> list[Notification]:
        """Evaluate active rules matching event.event_type and produce Notifications for resolved recipients."""
        rules = NotificationRule.objects.filter(
            tenant=event.tenant,
            event_type=event.event_type,
            is_active=True,
        ).select_related("target_role", "template")

        notifications_created = []

        for rule in rules:
            if not self._evaluate_condition(rule.condition_json, event.payload):
                continue

            recipients = self._resolve_recipients(event, rule)
            for user in recipients:
                if self._is_deduplicated_cooldown(event.tenant, user, event.event_type, rule.cooldown_minutes):
                    logger.info("Alert deduplicated for user %s on event %s (cooldown active)", user, event.event_type)
                    continue

                title = f"Alert: {event.event_type}"
                message = f"Event {event.event_number} occurred."
                if rule.template:
                    title, message = self.template_engine.render_template(rule.template, event.payload)

                not_num = self.number_generator.generate_notification_number(event.tenant)
                notif = Notification.objects.create(
                    tenant=event.tenant,
                    company=event.company,
                    branch=event.branch,
                    notification_number=not_num,
                    recipient=user,
                    title=title,
                    message=message,
                    channel=rule.channel,
                    priority=rule.priority,
                    status=NotificationStatus.PENDING,
                    source_event=event,
                    metadata=event.payload,
                )
                notifications_created.append(notif)

        return notifications_created

    def _evaluate_condition(self, condition: dict[str, Any], payload: dict[str, Any]) -> bool:
        """Evaluate simple condition rules against event payload."""
        if not condition:
            return True

        for key, val in condition.items():
            if key == "amount_gt":
                if Decimal(str(payload.get("amount", "0"))) <= Decimal(str(val)):
                    return False
            elif key == "stock_lt":
                if Decimal(str(payload.get("current_quantity", "0"))) >= Decimal(str(val)):
                    return False
            elif key == "days_until_expiry_lt":
                if int(payload.get("days_until_expiry", 999)) >= int(val):
                    return False
        return True

    def _resolve_recipients(self, event: DomainEvent, rule: NotificationRule) -> list[User]:
        """Resolve recipient users based on rule target_role or event actor."""
        if rule.target_role:
            users = list(User.objects.filter(role_assignments__role=rule.target_role, role_assignments__is_active=True).distinct())
            if users:
                return users
        if event.actor:
            return [event.actor]
        return list(User.objects.filter(is_superuser=True)[:5])

    def _is_deduplicated_cooldown(self, tenant: Any, user: User, event_type: str, cooldown_minutes: int) -> bool:
        """Check if an identical notification was generated for recipient within cooldown_minutes."""
        if cooldown_minutes <= 0:
            return False
        cutoff = timezone.now() - timezone.timedelta(minutes=cooldown_minutes)
        return Notification.objects.filter(
            tenant=tenant,
            recipient=user,
            source_event__event_type=event_type,
            created_at__gte=cutoff,
        ).exists()
