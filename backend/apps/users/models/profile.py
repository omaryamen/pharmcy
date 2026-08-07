"""Employee Profile model extending User identity with HR and workplace parameters."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", _("Full Time")
    PART_TIME = "part_time", _("Part Time")
    CONTRACT = "contract", _("Contract")
    INTERN = "intern", _("Intern")
    TEMPORARY = "temporary", _("Temporary")


class Gender(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")


class EmployeeProfile(FullAuditModel, TenantAwareModel):
    """HR and employment profile linked 1:1 to core.User."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name="User",
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="employee_profiles",
        null=True,
        blank=True,
        verbose_name="Company",
    )
    primary_branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="primary_employee_profiles",
        null=True,
        blank=True,
        verbose_name="Primary branch",
    )
    branches = models.ManyToManyField(
        "branches.Branch",
        related_name="employee_profiles",
        blank=True,
        verbose_name="Assigned branches",
    )

    employee_number = models.CharField(max_length=50, blank=True, default="", verbose_name="Employee number")
    arabic_name = models.CharField(max_length=200, blank=True, default="", verbose_name="Arabic name")
    english_name = models.CharField(max_length=200, blank=True, default="", verbose_name="English name")
    national_id = models.CharField(max_length=50, blank=True, default="", verbose_name="National ID")
    passport_number = models.CharField(max_length=50, blank=True, default="", verbose_name="Passport number")

    gender = models.CharField(max_length=20, choices=Gender.choices, blank=True, default="", verbose_name="Gender")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of birth")

    job_title = models.CharField(max_length=100, blank=True, default="", verbose_name="Job title")
    department = models.CharField(max_length=100, blank=True, default="", verbose_name="Department")
    employment_type = models.CharField(
        max_length=30,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        verbose_name="Employment type",
    )
    position = models.CharField(max_length=100, blank=True, default="", verbose_name="Position")
    job_grade = models.CharField(max_length=50, blank=True, default="", verbose_name="Job grade")

    hire_date = models.DateField(null=True, blank=True, verbose_name="Hire date")
    termination_date = models.DateField(null=True, blank=True, verbose_name="Termination date")

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
        verbose_name="Manager",
    )
    direct_supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervised_employees",
        verbose_name="Direct supervisor",
    )

    emergency_contact = models.JSONField(default=dict, blank=True, verbose_name="Emergency contact")
    mfa_enabled = models.BooleanField(default=False, verbose_name="MFA enabled")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")

    class Meta:
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "employee_number"],
                condition=models.Q(employee_number__gt=""),
                name="users_emp_profile_tenant_emp_num_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"Profile for {self.user.email} ({self.user.full_name})"
