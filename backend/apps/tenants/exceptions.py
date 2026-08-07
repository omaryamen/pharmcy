"""Exceptions specific to Tenant Management."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError, PharmaCloudError


class TenantNotFoundError(NotFoundError):
    code = "tenant_not_found"
    message = "The requested tenant does not exist."


class TenantStatusError(BusinessRuleViolation):
    code = "tenant_status_invalid"
    message = "The operation cannot be performed for the tenant in its current status."


class TenantLimitExceededError(BusinessRuleViolation):
    status_code = 403
    code = "tenant_limit_exceeded"
    message = "Tenant quota limit reached. Upgrade subscription plan to increase limit."


class DuplicateSlugError(ConflictError):
    code = "duplicate_tenant_slug"
    message = "A tenant with this slug already exists."


class DomainVerificationError(BusinessRuleViolation):
    code = "domain_verification_failed"
    message = "Domain verification failed or domain is unavailable."


class InvalidSubscriptionError(BusinessRuleViolation):
    code = "invalid_subscription"
    message = "Invalid subscription plan configuration or date range."
