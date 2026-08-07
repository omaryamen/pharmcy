"""Django Admin configuration for Employee Profiles."""

from __future__ import annotations

from django.contrib import admin

from apps.users.models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "employee_number", "company", "primary_branch", "job_title", "department", "employment_type"]
    list_filter = ["employment_type", "department", "gender"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "employee_number", "national_id"]
