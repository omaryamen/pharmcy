"""Customer service managing customer identity, financial profiles, lifecycle and relationships."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from django.db import transaction

from apps.customers.exceptions import (
    CustomerAddressNotFoundError,
    CustomerDeleteForbiddenError,
    CustomerMedicalProfileNotFoundError,
    CustomerNotFoundError,
    DuplicateCustomerCodeError,
    DuplicateCustomerNumberError,
    InvalidCreditLimitError,
)
from apps.customers.models import Customer, CustomerAddress, CustomerMedicalProfile, CustomerStatus
from apps.customers.repositories import (
    CustomerAddressRepository,
    CustomerMedicalProfileRepository,
    CustomerRepository,
)
from apps.customers.validators import validate_credit_limit, validate_date_range

logger = logging.getLogger(__name__)


class CustomerService:
    def __init__(self) -> None:
        self.repository = CustomerRepository()
        self.address_repository = CustomerAddressRepository()
        self.medical_repository = CustomerMedicalProfileRepository()

    @transaction.atomic
    def create_customer(
        self,
        tenant,
        *,
        code: str | None = None,
        customer_number: str | None = None,
        customer_type: str = "individual",
        company=None,
        preferred_branch=None,
        first_name: str = "",
        middle_name: str = "",
        last_name: str = "",
        arabic_name: str = "",
        english_name: str = "",
        preferred_name: str = "",
        gender: str = "unspecified",
        date_of_birth=None,
        national_id: str = "",
        passport_number: str = "",
        nationality: str = "Yemeni",
        occupation: str = "",
        profile_photo=None,
        phone: str = "",
        secondary_phone: str = "",
        mobile: str = "",
        whatsapp: str = "",
        email: str = "",
        alternative_email: str = "",
        preferred_contact_method: str = "phone",
        preferred_communication_language: str = "en",
        preferred_language: str = "en",
        preferred_currency: str = "YER",
        preferred_payment_method: str = "cash",
        sms_notifications: bool = True,
        email_notifications: bool = True,
        whatsapp_notifications: bool = True,
        marketing_consent: bool = False,
        notification_preferences: dict | None = None,
        credit_allowed: bool = False,
        credit_limit=0.00,
        payment_terms: str = "Immediate",
        opening_balance=0.00,
        current_balance=0.00,
        credit_status: str = "normal",
        default_payment_method: str = "cash",
        tax_category: str = "standard",
        discount_eligibility: bool = True,
        discount_percentage=0.00,
        price_list: str = "",
        customer_group: str = "regular",
        customer_segment: str = "",
        customer_category: str = "",
        loyalty_account_number: str = "",
        loyalty_points_balance=0.00,
        membership_level: str = "bronze",
        membership_number: str = "",
        loyalty_enrollment_date=None,
        loyalty_expiration_date=None,
        insurance_provider_name: str = "",
        insurance_policy_number: str = "",
        insurance_member_number: str = "",
        insurance_coverage_status: str = "none",
        insurance_coverage_start_date=None,
        insurance_coverage_end_date=None,
        insurance_category: str = "",
        notes: str = "",
        medical_profile_data: dict | None = None,
        addresses_data: list[dict] | None = None,
        **extra_fields,
    ) -> Customer:
        # Validate credit limit
        validate_credit_limit(credit_limit)
        if credit_limit < 0:
            raise InvalidCreditLimitError()

        # Validate insurance dates if present
        validate_date_range(
            insurance_coverage_start_date,
            insurance_coverage_end_date,
            "Insurance start date must be before end date.",
        )

        # Generate unique code and number if not provided
        clean_code = code.lower().strip() if code else f"cus-{uuid.uuid4().hex[:8]}"
        clean_number = customer_number.strip() if customer_number else f"CN-{uuid.uuid4().hex[:8].upper()}"

        if self.repository.exists(tenant=tenant, code=clean_code):
            raise DuplicateCustomerCodeError(f"A customer with code '{clean_code}' already exists in this tenant.")

        if self.repository.exists(tenant=tenant, customer_number=clean_number):
            raise DuplicateCustomerNumberError(f"A customer with customer number '{clean_number}' already exists in this tenant.")

        customer = self.repository.create(
            tenant=tenant,
            company=company,
            preferred_branch=preferred_branch,
            code=clean_code,
            customer_number=clean_number,
            customer_type=customer_type,
            status=CustomerStatus.ACTIVE,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            arabic_name=arabic_name,
            english_name=english_name,
            preferred_name=preferred_name,
            gender=gender,
            date_of_birth=date_of_birth,
            national_id=national_id,
            passport_number=passport_number,
            nationality=nationality,
            occupation=occupation,
            profile_photo=profile_photo,
            phone=phone,
            secondary_phone=secondary_phone,
            mobile=mobile,
            whatsapp=whatsapp,
            email=email,
            alternative_email=alternative_email,
            preferred_contact_method=preferred_contact_method,
            preferred_communication_language=preferred_communication_language,
            preferred_language=preferred_language,
            preferred_currency=preferred_currency,
            preferred_payment_method=preferred_payment_method,
            sms_notifications=sms_notifications,
            email_notifications=email_notifications,
            whatsapp_notifications=whatsapp_notifications,
            marketing_consent=marketing_consent,
            notification_preferences=notification_preferences or {},
            credit_allowed=credit_allowed,
            credit_limit=credit_limit,
            payment_terms=payment_terms,
            opening_balance=opening_balance,
            current_balance=current_balance,
            credit_status=credit_status,
            default_payment_method=default_payment_method,
            tax_category=tax_category,
            discount_eligibility=discount_eligibility,
            discount_percentage=discount_percentage,
            price_list=price_list,
            customer_group=customer_group,
            customer_segment=customer_segment,
            customer_category=customer_category,
            loyalty_account_number=loyalty_account_number,
            loyalty_points_balance=loyalty_points_balance,
            membership_level=membership_level,
            membership_number=membership_number,
            loyalty_enrollment_date=loyalty_enrollment_date,
            loyalty_expiration_date=loyalty_expiration_date,
            insurance_provider_name=insurance_provider_name,
            insurance_policy_number=insurance_policy_number,
            insurance_member_number=insurance_member_number,
            insurance_coverage_status=insurance_coverage_status,
            insurance_coverage_start_date=insurance_coverage_start_date,
            insurance_coverage_end_date=insurance_coverage_end_date,
            insurance_category=insurance_category,
            notes=notes,
            **extra_fields,
        )

        # Create/update optional medical profile foundation
        if medical_profile_data is not None:
            self.update_medical_profile(tenant, customer, **medical_profile_data)

        # Create optional initial addresses
        if addresses_data:
            for addr_data in addresses_data:
                self.add_address(tenant, customer, **addr_data)

        logger.info("Created customer %s (%s) for tenant %s", customer.display_name, customer.code, tenant.slug)
        return customer

    @transaction.atomic
    def update_customer(self, customer: Customer, **fields) -> Customer:
        if "credit_limit" in fields:
            validate_credit_limit(fields["credit_limit"])
            if fields["credit_limit"] < 0:
                raise InvalidCreditLimitError()

        if "insurance_coverage_start_date" in fields or "insurance_coverage_end_date" in fields:
            start_date = fields.get("insurance_coverage_start_date", customer.insurance_coverage_start_date)
            end_date = fields.get("insurance_coverage_end_date", customer.insurance_coverage_end_date)
            validate_date_range(start_date, end_date, "Insurance start date must be before end date.")

        updated = self.repository.update(customer, **fields)
        logger.info("Updated customer %s", customer.code)
        return updated

    @transaction.atomic
    def activate_customer(self, customer: Customer) -> Customer:
        customer.activate()
        logger.info("Activated customer %s", customer.code)
        return customer

    @transaction.atomic
    def deactivate_customer(self, customer: Customer) -> Customer:
        customer.deactivate()
        logger.info("Deactivated customer %s", customer.code)
        return customer

    @transaction.atomic
    def block_customer(self, customer: Customer) -> Customer:
        customer.block()
        logger.info("Blocked customer %s", customer.code)
        return customer

    @transaction.atomic
    def unblock_customer(self, customer: Customer) -> Customer:
        customer.unblock()
        logger.info("Unblocked customer %s", customer.code)
        return customer

    @transaction.atomic
    def suspend_customer(self, customer: Customer) -> Customer:
        customer.suspend()
        logger.info("Suspended customer %s", customer.code)
        return customer

    @transaction.atomic
    def restore_customer(self, customer: Customer) -> Customer:
        customer.restore()
        logger.info("Restored customer %s", customer.code)
        return customer

    @transaction.atomic
    def soft_delete_customer(self, customer: Customer) -> Customer:
        # Dependency checks for sales, invoices, prescriptions, ledger
        has_sales = getattr(customer, "sales", None) and customer.sales.filter(is_deleted=False).exists()
        has_invoices = getattr(customer, "invoices", None) and customer.invoices.filter(is_deleted=False).exists()
        has_prescriptions = getattr(customer, "prescriptions", None) and customer.prescriptions.filter(is_deleted=False).exists()

        if has_sales or has_invoices or has_prescriptions:
            raise CustomerDeleteForbiddenError("Cannot delete customer linked to active sales, invoices, or prescriptions.")

        self.repository.delete(customer)
        logger.info("Soft deleted customer %s", customer.code)
        return customer

    @transaction.atomic
    def add_address(self, tenant, customer: Customer, **address_fields) -> CustomerAddress:
        address = self.address_repository.create(tenant=tenant, customer=customer, **address_fields)
        logger.info("Added address %s for customer %s", address.pk, customer.code)
        return address

    @transaction.atomic
    def update_address(self, address: CustomerAddress, **address_fields) -> CustomerAddress:
        updated = self.address_repository.update(address, **address_fields)
        logger.info("Updated address %s for customer %s", address.pk, address.customer.code)
        return updated

    @transaction.atomic
    def delete_address(self, address: CustomerAddress) -> None:
        self.address_repository.delete(address)
        logger.info("Deleted address %s", address.pk)

    @transaction.atomic
    def update_medical_profile(self, tenant, customer: Customer, **medical_fields) -> CustomerMedicalProfile:
        medical_profile, created = CustomerMedicalProfile.objects.get_or_create(
            tenant=tenant, customer=customer, defaults=medical_fields
        )
        if not created:
            medical_profile = self.medical_repository.update(medical_profile, **medical_fields)
        customer.medical_profile = medical_profile
        logger.info("Updated medical profile for customer %s", customer.code)
        return medical_profile
