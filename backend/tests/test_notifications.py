"""Comprehensive Test Suite for Enterprise Notifications & Automation Engine (IMP-033 / apps.notifications)."""

import uuid
from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.models import Tenant
from apps.companies.models import Company
from apps.branches.models import Branch
from apps.notifications.exceptions import UnsafeWebhookUrlError
from apps.notifications.models import (
    DeadLetterEvent,
    DomainEvent,
    EventStatus,
    EventTypeChoices,
    Notification,
    NotificationChannel,
    NotificationDelivery,
    NotificationPriority,
    NotificationRule,
    NotificationStatus,
    NotificationTemplate,
    OutboxEvent,
    WebhookEndpoint,
)
from apps.notifications.selectors import NotificationSelector
from apps.notifications.services import (
    EventPublisherService,
    NotificationDeliveryService,
    RuleEngineService,
    TemplateEngineService,
)

User = get_user_model()


def notif_setup():
    """Helper setup creating tenant, company, branch, and user."""
    uid = uuid.uuid4().hex[:6]
    tenant = Tenant.objects.create(name=f"NOTIF Tenant {uid}", code=f"TNT-{uid}", slug=f"notif-slug-{uid}")
    company = Company.objects.create(tenant=tenant, legal_name="Pharma Cloud Corp", commercial_name="Pharma Cloud Corp", code=f"COMP-{uid[:4]}", slug=f"comp-{uid[:4]}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Main Pharmacy Branch", code=f"BR-{uid[:4]}")
    user = User.objects.create_user(email=f"user_{uid}@test.com", first_name="Manager", last_name="Alice", password="pass")
    return tenant, company, branch, user


@pytest.mark.django_db
class TestEventPublisherService:
    """Test suite for EventPublisherService and idempotency rules."""

    def test_publish_event_creates_domain_and_outbox_event(self):
        tenant, company, branch, user = notif_setup()
        publisher = EventPublisherService()

        evt = publisher.publish_event(
            tenant=tenant,
            company=company,
            branch=branch,
            event_type=EventTypeChoices.MEDICINE_LOW_STOCK,
            source_module="inventory",
            source_object_id="MED-001",
            payload={"medicine_name": "Amoxicillin", "current_quantity": 5},
            actor=user,
            idempotency_key=f"low-stock-{uuid.uuid4().hex[:6]}",
        )

        assert evt.event_number.startswith("EVT-")
        assert evt.status == EventStatus.PENDING
        assert OutboxEvent.objects.filter(domain_event=evt).exists()

    def test_event_idempotency_prevents_duplicates(self):
        tenant, company, branch, user = notif_setup()
        publisher = EventPublisherService()
        key = f"idempotent-key-{uuid.uuid4().hex[:6]}"

        evt1 = publisher.publish_event(
            tenant=tenant,
            company=company,
            branch=branch,
            event_type=EventTypeChoices.MEDICINE_LOW_STOCK,
            source_module="inventory",
            source_object_id="MED-001",
            payload={"current_quantity": 5},
            idempotency_key=key,
        )

        evt2 = publisher.publish_event(
            tenant=tenant,
            company=company,
            branch=branch,
            event_type=EventTypeChoices.MEDICINE_LOW_STOCK,
            source_module="inventory",
            source_object_id="MED-001",
            payload={"current_quantity": 5},
            idempotency_key=key,
        )

        assert evt1.pk == evt2.pk
        assert DomainEvent.objects.filter(tenant=tenant, idempotency_key=key).count() == 1


@pytest.mark.django_db
class TestTemplateEngineService:
    """Test suite for safe template variable substitution."""

    def test_render_template_variable_substitution(self, tenant):
        tmpl = NotificationTemplate.objects.create(
            tenant=tenant,
            code="TMPL-LOW-STOCK",
            name="Low Stock Alert",
            event_type=EventTypeChoices.MEDICINE_LOW_STOCK,
            language="en",
            subject_template="Low Stock Warning: {{medicine_name}}",
            body_template="Medicine {{medicine_name}} has reached low stock level (Current: {{quantity}}).",
        )

        engine = TemplateEngineService()
        subject, body = engine.render_template(tmpl, {"medicine_name": "Paracetamol 500mg", "quantity": 10})

        assert subject == "Low Stock Warning: Paracetamol 500mg"
        assert body == "Medicine Paracetamol 500mg has reached low stock level (Current: 10)."


@pytest.mark.django_db
class TestRuleEngineServiceAndDeduplication:
    """Test suite for rule engine evaluation and alert deduplication cooldown."""

    def test_evaluate_event_rules_generates_notifications(self):
        tenant, company, branch, user = notif_setup()
        publisher = EventPublisherService()
        rule_engine = RuleEngineService()

        # Create Rule
        NotificationRule.objects.create(
            tenant=tenant,
            company=company,
            code="RULE-LOW-STOCK",
            name="Low Stock Notification Rule",
            event_type=EventTypeChoices.MEDICINE_LOW_STOCK,
            condition_json={"stock_lt": 10},
            channel=NotificationChannel.IN_APP,
            priority=NotificationPriority.HIGH,
            cooldown_minutes=15,
        )

        evt = publisher.publish_event(
            tenant=tenant,
            company=company,
            branch=branch,
            event_type=EventTypeChoices.MEDICINE_LOW_STOCK,
            source_module="inventory",
            source_object_id="MED-002",
            payload={"current_quantity": 4},
            actor=user,
        )

        notifs = rule_engine.evaluate_event_rules(evt)
        assert len(notifs) == 1
        assert notifs[0].recipient == user
        assert notifs[0].priority == NotificationPriority.HIGH

        # Verify Deduplication Cooldown (Second event within 15 min does not generate duplicate notification for user)
        evt2 = publisher.publish_event(
            tenant=tenant,
            company=company,
            branch=branch,
            event_type=EventTypeChoices.MEDICINE_LOW_STOCK,
            source_module="inventory",
            source_object_id="MED-002",
            payload={"current_quantity": 3},
            actor=user,
        )
        notifs2 = rule_engine.evaluate_event_rules(evt2)
        assert len(notifs2) == 0


@pytest.mark.django_db
class TestNotificationDeliveryServiceAndSecurity:
    """Test suite for NotificationDeliveryService, Webhook SSRF protection, and Dead Letter Queue."""

    def test_in_app_delivery_updates_status(self):
        tenant, company, branch, user = notif_setup()
        delivery_service = NotificationDeliveryService()

        notif = Notification.objects.create(
            tenant=tenant,
            company=company,
            branch=branch,
            notification_number="NOT-TEST-001",
            recipient=user,
            title="System Alert",
            message="Your report is ready.",
            channel=NotificationChannel.IN_APP,
            status=NotificationStatus.PENDING,
        )

        deliv = delivery_service.deliver_notification(notif)
        notif.refresh_from_db()
        assert notif.status == NotificationStatus.DELIVERED
        assert deliv.status == NotificationStatus.DELIVERED

    def test_webhook_ssrf_protection_rejects_localhost(self):
        delivery_service = NotificationDeliveryService()
        with pytest.raises(UnsafeWebhookUrlError):
            delivery_service._validate_webhook_url_security("http://localhost:8000/webhook/")

        with pytest.raises(UnsafeWebhookUrlError):
            delivery_service._validate_webhook_url_security("http://127.0.0.1/webhook/")

    def test_move_to_dead_letter_queue(self):
        tenant, company, branch, user = notif_setup()
        publisher = EventPublisherService()
        delivery_service = NotificationDeliveryService()

        evt = publisher.publish_event(
            tenant=tenant,
            company=company,
            event_type=EventTypeChoices.SYSTEM_ERROR,
            source_module="core",
            source_object_id="SYS-001",
            payload={"error": "Database timeout"},
        )

        dle = delivery_service.move_to_dead_letter(evt, failure_reason="Unrecoverable connection failure")
        evt.refresh_from_db()

        assert evt.status == EventStatus.DEAD_LETTER
        assert dle.dead_letter_number.startswith("DLE-")
        assert dle.is_resolved is False


@pytest.mark.django_db
class TestTenantIsolationInNotifications:
    """Test suite ensuring strict multi-tenant isolation for notifications."""

    def test_notification_tenant_isolation(self):
        tenant1, company1, branch1, user1 = notif_setup()
        uid2 = uuid.uuid4().hex[:6]
        tenant2 = Tenant.objects.create(name=f"NOTIF Tenant 2 {uid2}", code=f"TNT-{uid2}", slug=f"notif-slug-2-{uid2}")

        notif1 = Notification.objects.create(
            tenant=tenant1,
            company=company1,
            branch=branch1,
            notification_number="NOT-T1-001",
            recipient=user1,
            title="Tenant 1 Alert",
            message="Private alert",
            channel=NotificationChannel.IN_APP,
            status=NotificationStatus.PENDING,
        )

        selector = NotificationSelector()
        t1_count = selector.get_unread_count(tenant1, user1)
        t2_count = selector.get_unread_count(tenant2, user1)

        assert t1_count == 1
        assert t2_count == 0
