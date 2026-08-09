"""Customer duplicate detection service providing safe non-destructive matching logic."""

from __future__ import annotations

from typing import Any

from django.db.models import Q

from apps.customers.models import Customer
from apps.customers.repositories import CustomerRepository


class CustomerDuplicateDetector:
    def __init__(self) -> None:
        self.repository = CustomerRepository()

    def detect_duplicates(
        self,
        tenant,
        *,
        phone: str = "",
        mobile: str = "",
        email: str = "",
        national_id: str = "",
        passport_number: str = "",
        insurance_member_number: str = "",
        first_name: str = "",
        last_name: str = "",
        arabic_name: str = "",
        english_name: str = "",
        exclude_customer_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Inspects tenant's customer database for duplicate candidates matching key identity criteria.

        Does NOT perform automatic merge operations.
        Returns a list of structured match results with confidence score and match reasons.
        """
        duplicates: dict[str, dict[str, Any]] = {}

        def add_candidate(customer: Customer, reason: str, weight: int):
            cid = str(customer.pk)
            if cid not in duplicates:
                duplicates[cid] = {
                    "id": cid,
                    "code": customer.code,
                    "customer_number": customer.customer_number,
                    "display_name": customer.display_name,
                    "phone": customer.phone,
                    "mobile": customer.mobile,
                    "email": customer.email,
                    "national_id": customer.national_id,
                    "status": customer.status,
                    "confidence_score": 0,
                    "match_reasons": [],
                }
            if reason not in duplicates[cid]["match_reasons"]:
                duplicates[cid]["match_reasons"].append(reason)
                duplicates[cid]["confidence_score"] += weight

        qs = self.repository.filter(tenant=tenant)
        if exclude_customer_id:
            qs = qs.exclude(pk=exclude_customer_id)

        # 1. Exact National ID match (100% confidence)
        if national_id and national_id.strip():
            nat_id_clean = national_id.strip()
            for c in qs.filter(national_id=nat_id_clean):
                add_candidate(c, f"Exact National ID match ('{nat_id_clean}')", 100)

        # 2. Exact Passport Number match (100% confidence)
        if passport_number and passport_number.strip():
            pass_clean = passport_number.strip()
            for c in qs.filter(passport_number=pass_clean):
                add_candidate(c, f"Exact Passport Number match ('{pass_clean}')", 100)

        # 3. Exact Insurance Member Number match (90% confidence)
        if insurance_member_number and insurance_member_number.strip():
            ins_clean = insurance_member_number.strip()
            for c in qs.filter(insurance_member_number=ins_clean):
                add_candidate(c, f"Exact Insurance Member Number match ('{ins_clean}')", 90)

        # 4. Phone / Mobile match (80% confidence)
        phones_to_check = [p.strip() for p in [phone, mobile] if p and p.strip()]
        for p in phones_to_check:
            for c in qs.filter(Q(phone=p) | Q(mobile=p) | Q(secondary_phone=p) | Q(whatsapp=p)):
                add_candidate(c, f"Phone/Mobile match ('{p}')", 80)

        # 5. Email match (75% confidence)
        if email and email.strip():
            email_clean = email.strip().lower()
            for c in qs.filter(Q(email__iexact=email_clean) | Q(alternative_email__iexact=email_clean)):
                add_candidate(c, f"Email address match ('{email_clean}')", 75)

        # 6. Name similarity (50% confidence)
        if arabic_name and arabic_name.strip():
            for c in qs.filter(arabic_name__icontains=arabic_name.strip()):
                add_candidate(c, f"Arabic name similarity ('{arabic_name.strip()}')", 50)

        if english_name and english_name.strip():
            for c in qs.filter(english_name__icontains=english_name.strip()):
                add_candidate(c, f"English name similarity ('{english_name.strip()}')", 50)

        if first_name and last_name:
            full = f"{first_name.strip()} {last_name.strip()}"
            for c in qs.filter(first_name__icontains=first_name.strip(), last_name__icontains=last_name.strip()):
                add_candidate(c, f"First & Last name match ('{full}')", 60)

        # Return candidates sorted by confidence score (highest first)
        results = sorted(duplicates.values(), key=lambda x: x["confidence_score"], reverse=True)
        return results
