"""Unit & Integration tests for Enterprise Customer Management services."""

import pytest
from apps.core.models import Tenant
from apps.customers.exceptions import (
    CustomerDeleteForbiddenError,
    DuplicateCustomerCodeError,
    DuplicateCustomerNumberError,
    InvalidCreditLimitError,
)
from apps.customers.services import CustomerService


@pytest.mark.django_db
class TestCustomerServices:
    def test_create_and_update_customer_service(self, db):
        tenant = Tenant.objects.create(name="Tenant Cus Serv", code="t_cus_srv", slug="tenant-cus-srv")
        service = CustomerService()

        customer = service.create_customer(
            tenant=tenant,
            code="CUS-100",
            customer_number="CN-100",
            first_name="Hassan",
            last_name="Ali",
            email="hassan@example.com",
            phone="+967770001122",
            credit_limit=500.00,
        )

        assert customer.code == "cus-100"
        assert customer.customer_number == "CN-100"
        assert customer.first_name == "Hassan"

        updated = service.update_customer(customer, phone="+967779998877", credit_limit=1500.00)
        assert updated.phone == "+967779998877"
        assert updated.credit_limit == 1500.00

    def test_duplicate_code_and_number_prevention(self, db):
        tenant = Tenant.objects.create(name="Tenant Cus Dup", code="t_cus_d", slug="tenant-cus-d")
        service = CustomerService()

        service.create_customer(tenant=tenant, code="CUS-DUP", customer_number="CN-DUP", first_name="User1")

        with pytest.raises(DuplicateCustomerCodeError):
            service.create_customer(tenant=tenant, code="CUS-DUP", customer_number="CN-NEW", first_name="User2")

        with pytest.raises(DuplicateCustomerNumberError):
            service.create_customer(tenant=tenant, code="CUS-NEW", customer_number="CN-DUP", first_name="User3")

    def test_negative_credit_limit_validation(self, db):
        tenant = Tenant.objects.create(name="Tenant Cus Credit", code="t_cus_cr", slug="tenant-cus-cr")
        service = CustomerService()

        with pytest.raises(InvalidCreditLimitError):
            service.create_customer(tenant=tenant, code="CUS-NEG", customer_number="CN-NEG", credit_limit=-100.00)

    def test_medical_profile_and_addresses_creation(self, db):
        tenant = Tenant.objects.create(name="Tenant Cus Med", code="t_cus_m", slug="tenant-cus-m")
        service = CustomerService()

        customer = service.create_customer(
            tenant=tenant,
            code="CUS-MED",
            customer_number="CN-MED",
            first_name="Doctor",
            last_name="Patient",
            medical_profile_data={
                "blood_type": "O+",
                "allergies": ["Penicillin"],
                "chronic_conditions": ["Hypertension"],
            },
            addresses_data=[
                {"address_type": "home", "city": "Sanaa", "is_primary": True},
            ],
        )

        assert hasattr(customer, "medical_profile")
        assert customer.medical_profile.blood_type == "O+"
        assert "Penicillin" in customer.medical_profile.allergies
        assert customer.addresses.count() == 1
        assert customer.addresses.first().city == "Sanaa"
