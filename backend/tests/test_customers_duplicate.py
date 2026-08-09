"""Tests for customer duplicate detection mechanism."""

import pytest
from apps.core.models import Tenant
from apps.customers.services import CustomerDuplicateDetector, CustomerService


@pytest.mark.django_db
class TestCustomerDuplicateDetection:
    def test_duplicate_detection_phone_email_national_id(self, db):
        tenant = Tenant.objects.create(name="Dup Tenant", code="dup_t", slug="dup-t")
        service = CustomerService()
        detector = CustomerDuplicateDetector()

        c1 = service.create_customer(
            tenant=tenant,
            code="CUS-DUP-1",
            customer_number="CN-DUP-1",
            first_name="Faisal",
            last_name="Omar",
            phone="+967770112233",
            email="faisal@example.com",
            national_id="1234567890",
        )

        duplicates = detector.detect_duplicates(
            tenant=tenant,
            phone="+967770112233",
            email="faisal@example.com",
            national_id="1234567890",
        )

        assert len(duplicates) == 1
        candidate = duplicates[0]
        assert candidate["id"] == str(c1.pk)
        assert candidate["confidence_score"] >= 100
        assert len(candidate["match_reasons"]) >= 3

    def test_duplicate_detection_exclusion(self, db):
        tenant = Tenant.objects.create(name="Dup Exclude Tenant", code="dup_ex", slug="dup-ex")
        service = CustomerService()
        detector = CustomerDuplicateDetector()

        c1 = service.create_customer(
            tenant=tenant,
            code="CUS-DUP-2",
            customer_number="CN-DUP-2",
            phone="+967770999999",
        )

        duplicates = detector.detect_duplicates(
            tenant=tenant,
            phone="+967770999999",
            exclude_customer_id=str(c1.pk),
        )

        assert len(duplicates) == 0
