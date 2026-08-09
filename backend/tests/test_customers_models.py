"""Unit tests for Customer domain models and lifecycle transitions."""

import pytest
from apps.core.models import Tenant
from apps.customers.models import Customer, CustomerAddress, CustomerMedicalProfile, CustomerStatus, CreditStatus


@pytest.mark.django_db
class TestCustomerModels:
    def test_customer_model_creation_and_defaults(self, db):
        tenant = Tenant.objects.create(name="Customer Model Tenant", code="c_mod_t", slug="c-mod-t")
        customer = Customer.objects.create(
            tenant=tenant,
            code="cus-001",
            customer_number="CN-001",
            first_name="Ahmed",
            last_name="Al-Mansoor",
            arabic_name="أحمد المنصور",
            phone="+967771234567",
            email="ahmed@example.com",
            credit_limit=1000.00,
        )

        assert customer.code == "cus-001"
        assert customer.customer_number == "CN-001"
        assert customer.display_name == "أحمد المنصور"
        assert customer.status == CustomerStatus.ACTIVE
        assert customer.credit_allowed is False
        assert customer.is_deleted is False

    def test_customer_status_transitions(self, db):
        tenant = Tenant.objects.create(name="Status Tenant", code="stat_t", slug="stat-t")
        customer = Customer.objects.create(
            tenant=tenant,
            code="cus-002",
            customer_number="CN-002",
            first_name="Sara",
            last_name="Salem",
        )

        customer.block()
        assert customer.status == CustomerStatus.BLOCKED
        assert customer.credit_status == CreditStatus.BLOCKED

        customer.unblock()
        assert customer.status == CustomerStatus.ACTIVE
        assert customer.credit_status == CreditStatus.NORMAL

        customer.suspend()
        assert customer.status == CustomerStatus.SUSPENDED

        customer.activate()
        assert customer.status == CustomerStatus.ACTIVE

        customer.delete()
        assert customer.is_deleted is True
        assert customer.deleted_at is not None

        customer.restore()
        assert customer.is_deleted is False
        assert customer.status == CustomerStatus.ACTIVE

    def test_customer_address_save_flags(self, db):
        tenant = Tenant.objects.create(name="Address Tenant", code="addr_t", slug="addr-t")
        customer = Customer.objects.create(
            tenant=tenant,
            code="cus-addr",
            customer_number="CN-ADDR",
        )

        addr1 = CustomerAddress.objects.create(
            tenant=tenant,
            customer=customer,
            address_type="home",
            city="Sanaa",
            is_primary=True,
        )
        assert addr1.is_primary is True

        addr2 = CustomerAddress.objects.create(
            tenant=tenant,
            customer=customer,
            address_type="work",
            city="Aden",
            is_primary=True,
        )
        addr1.refresh_from_db()
        assert addr2.is_primary is True
        assert addr1.is_primary is False
