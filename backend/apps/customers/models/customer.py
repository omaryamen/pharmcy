"""Customer Domain Model representing individual and organizational clients."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.customers.models.enums import (
    CreditStatus,
    CustomerStatus,
    CustomerType,
    Gender,
    InsuranceCoverageStatus,
)


class Customer(FullAuditModel, TenantAwareModel):
    """Enterprise Customer Entity supporting individual and organizational profiles."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="customers",
        null=True,
        blank=True,
        verbose_name=_("Company"),
        db_index=True,
    )
    preferred_branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="preferred_customers",
        null=True,
        blank=True,
        verbose_name=_("Preferred branch"),
        db_index=True,
    )

    # 1. Customer Identity
    code = models.CharField(max_length=50, verbose_name=_("Customer code"))
    customer_number = models.CharField(max_length=50, verbose_name=_("Customer number"))
    customer_type = models.CharField(
        max_length=40,
        choices=CustomerType.choices,
        default=CustomerType.INDIVIDUAL,
        verbose_name=_("Customer type"),
    )
    status = models.CharField(
        max_length=30,
        choices=CustomerStatus.choices,
        default=CustomerStatus.ACTIVE,
        db_index=True,
        verbose_name=_("Status"),
    )

    # 2. Personal Information (for individual customers / contacts)
    first_name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("First name"))
    middle_name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Middle name"))
    last_name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Last name"))
    arabic_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Arabic name"))
    english_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("English name"))
    preferred_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Preferred name"))
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.UNSPECIFIED,
        verbose_name=_("Gender"),
    )
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date of birth"))
    national_id = models.CharField(max_length=100, blank=True, default="", verbose_name=_("National ID"))
    passport_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Passport number"))
    nationality = models.CharField(max_length=100, blank=True, default="Yemeni", verbose_name=_("Nationality"))
    occupation = models.CharField(max_length=150, blank=True, default="", verbose_name=_("Occupation"))
    profile_photo = models.ImageField(upload_to="customer_photos/", null=True, blank=True, verbose_name=_("Profile photo"))

    # 3. Contact Information
    phone = models.CharField(max_length=32, blank=True, default="", verbose_name=_("Primary phone"))
    secondary_phone = models.CharField(max_length=32, blank=True, default="", verbose_name=_("Secondary phone"))
    mobile = models.CharField(max_length=32, blank=True, default="", verbose_name=_("Mobile"))
    whatsapp = models.CharField(max_length=32, blank=True, default="", verbose_name=_("WhatsApp"))
    email = models.EmailField(blank=True, default="", verbose_name=_("Email"))
    alternative_email = models.EmailField(blank=True, default="", verbose_name=_("Alternative email"))
    preferred_contact_method = models.CharField(max_length=50, default="phone", verbose_name=_("Preferred contact method"))
    preferred_communication_language = models.CharField(
        max_length=10, default="en", verbose_name=_("Preferred communication language")
    )

    # 6. Customer Preferences
    preferred_language = models.CharField(max_length=10, default="en", verbose_name=_("Preferred language"))
    preferred_currency = models.CharField(max_length=10, default="YER", verbose_name=_("Preferred currency"))
    preferred_payment_method = models.CharField(max_length=50, default="cash", verbose_name=_("Preferred payment method"))
    sms_notifications = models.BooleanField(default=True, verbose_name=_("SMS notifications enabled"))
    email_notifications = models.BooleanField(default=True, verbose_name=_("Email notifications enabled"))
    whatsapp_notifications = models.BooleanField(default=True, verbose_name=_("WhatsApp notifications enabled"))
    marketing_consent = models.BooleanField(default=False, verbose_name=_("Marketing consent"))
    notification_preferences = models.JSONField(default=dict, blank=True, verbose_name=_("Notification preferences"))

    # 7. Financial Profile
    credit_allowed = models.BooleanField(default=False, verbose_name=_("Credit allowed"))
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name=_("Credit limit"))
    payment_terms = models.CharField(max_length=100, default="Immediate", verbose_name=_("Payment terms"))
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name=_("Opening balance"))
    current_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name=_("Current balance"))
    credit_status = models.CharField(
        max_length=30,
        choices=CreditStatus.choices,
        default=CreditStatus.NORMAL,
        verbose_name=_("Credit status"),
    )
    default_payment_method = models.CharField(max_length=50, default="cash", verbose_name=_("Default payment method"))
    tax_category = models.CharField(max_length=50, default="standard", verbose_name=_("Tax category"))
    discount_eligibility = models.BooleanField(default=True, verbose_name=_("Discount eligibility"))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name=_("Discount percentage"))
    price_list = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Price list"))

    # 8. Customer Classification
    customer_group = models.CharField(max_length=100, default="regular", db_index=True, verbose_name=_("Customer group"))
    customer_segment = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Customer segment"))
    customer_category = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Customer category"))

    # 9. Loyalty Foundation
    loyalty_account_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Loyalty account number"))
    loyalty_points_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name=_("Loyalty points balance"))
    membership_level = models.CharField(max_length=50, default="bronze", verbose_name=_("Membership level"))
    membership_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Membership number"))
    loyalty_enrollment_date = models.DateField(null=True, blank=True, verbose_name=_("Loyalty enrollment date"))
    loyalty_expiration_date = models.DateField(null=True, blank=True, verbose_name=_("Loyalty expiration date"))

    # 10. Insurance Foundation
    insurance_provider_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Insurance provider name"))
    insurance_policy_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Insurance policy number"))
    insurance_member_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Insurance member number"))
    insurance_coverage_status = models.CharField(
        max_length=30,
        choices=InsuranceCoverageStatus.choices,
        default=InsuranceCoverageStatus.NONE,
        verbose_name=_("Insurance coverage status"),
    )
    insurance_coverage_start_date = models.DateField(null=True, blank=True, verbose_name=_("Insurance coverage start date"))
    insurance_coverage_end_date = models.DateField(null=True, blank=True, verbose_name=_("Insurance coverage end date"))
    insurance_category = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Insurance category"))

    # General Notes
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="customers_customer_tenant_code_uniq"),
            models.UniqueConstraint(fields=["tenant", "customer_number"], name="customers_customer_tenant_number_uniq"),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "customer_group"]),
            models.Index(fields=["tenant", "phone"]),
            models.Index(fields=["tenant", "mobile"]),
            models.Index(fields=["tenant", "email"]),
            models.Index(fields=["tenant", "national_id"]),
            models.Index(fields=["tenant", "passport_number"]),
            models.Index(fields=["tenant", "insurance_member_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.code})"

    @property
    def display_name(self) -> str:
        if self.arabic_name:
            return self.arabic_name
        if self.english_name:
            return self.english_name
        full_name = f"{self.first_name} {self.last_name}".strip()
        if full_name:
            return full_name
        if self.preferred_name:
            return self.preferred_name
        return self.code

    def activate(self) -> None:
        self.status = CustomerStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def deactivate(self) -> None:
        self.status = CustomerStatus.INACTIVE
        self.save(update_fields=["status", "updated_at"])

    def block(self) -> None:
        self.status = CustomerStatus.BLOCKED
        self.credit_status = CreditStatus.BLOCKED
        self.save(update_fields=["status", "credit_status", "updated_at"])

    def unblock(self) -> None:
        self.status = CustomerStatus.ACTIVE
        self.credit_status = CreditStatus.NORMAL
        self.save(update_fields=["status", "credit_status", "updated_at"])

    def suspend(self) -> None:
        self.status = CustomerStatus.SUSPENDED
        self.credit_status = CreditStatus.SUSPENDED
        self.save(update_fields=["status", "credit_status", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
        self.status = CustomerStatus.ACTIVE
        self.save(update_fields=["status", "is_deleted", "deleted_at", "updated_at"])
