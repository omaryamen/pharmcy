"""Branch service for business logic and lifecycle management."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils.text import slugify

from apps.branches.exceptions import (
    BranchDeleteForbiddenError,
    CompanyMismatchError,
    DuplicateBranchCodeError,
)
from apps.branches.models import Branch, BranchStatus
from apps.branches.repositories import BranchRepository, BranchSettingsRepository

logger = logging.getLogger(__name__)


class BranchService:
    def __init__(self) -> None:
        self.repository = BranchRepository()
        self.settings_repository = BranchSettingsRepository()

    @transaction.atomic
    def create_branch(
        self,
        tenant,
        company,
        *,
        name: str,
        code: str | None = None,
        slug: str | None = None,
        display_name: str = "",
        branch_type: str = "retail_pharmacy",
        country: str = "Yemen",
        city: str = "",
        manager=None,
        **extra_fields,
    ) -> Branch:
        if company.tenant_id != tenant.pk:
            raise CompanyMismatchError("Company does not belong to the current tenant.")

        clean_slug = slugify(slug or name)
        clean_code = (code or clean_slug).lower().replace("-", "_")

        if self.repository.exists(company=company, name=name):
            raise DuplicateBranchCodeError(f"A branch named '{name}' already exists in this company.", field="name")
        if self.repository.exists(company=company, code=clean_code):
            raise DuplicateBranchCodeError(f"A branch with code '{clean_code}' already exists in this company.", field="code")

        branch = self.repository.create(
            tenant=tenant,
            company=company,
            name=name,
            display_name=display_name or name,
            code=clean_code,
            slug=clean_slug,
            branch_type=branch_type,
            country=country,
            city=city,
            manager=manager,
            status=BranchStatus.ACTIVE,
            **extra_fields,
        )

        # Create default branch settings
        self.settings_repository.create(
            branch=branch,
            company=company,
            tenant=tenant,
        )

        logger.info("Created branch %s (%s) for company %s", branch.name, branch.code, company.code)
        return branch

    @transaction.atomic
    def update_branch(self, branch: Branch, **fields) -> Branch:
        return self.repository.update(branch, **fields)

    @transaction.atomic
    def activate_branch(self, branch: Branch) -> Branch:
        branch.activate()
        logger.info("Activated branch %s", branch.code)
        return branch

    @transaction.atomic
    def deactivate_branch(self, branch: Branch) -> Branch:
        branch.deactivate()
        logger.info("Deactivated branch %s", branch.code)
        return branch

    @transaction.atomic
    def suspend_branch(self, branch: Branch) -> Branch:
        branch.suspend()
        logger.info("Suspended branch %s", branch.code)
        return branch

    @transaction.atomic
    def archive_branch(self, branch: Branch) -> Branch:
        branch.archive()
        logger.info("Archived branch %s", branch.code)
        return branch

    @transaction.atomic
    def restore_branch(self, branch: Branch) -> Branch:
        branch.restore()
        logger.info("Restored branch %s", branch.code)
        return branch

    @transaction.atomic
    def soft_delete_branch(self, branch: Branch) -> Branch:
        # Check active dependencies guard
        has_inventory = getattr(branch, "inventory_items", None) and branch.inventory_items.filter(is_deleted=False).exists()
        has_sales = getattr(branch, "sales", None) and branch.sales.filter(is_deleted=False).exists()
        has_employees = getattr(branch, "employees", None) and branch.employees.filter(is_deleted=False).exists()

        if has_inventory or has_sales or has_employees:
            raise BranchDeleteForbiddenError("Cannot delete branch with active inventory, sales, or employees.")

        self.repository.delete(branch)
        logger.info("Soft deleted branch %s", branch.code)
        return branch

    @transaction.atomic
    def assign_manager(self, branch: Branch, manager) -> Branch:
        branch.manager = manager
        branch.save(update_fields=["manager", "updated_at"])
        logger.info("Assigned manager %s to branch %s", manager, branch.code)
        return branch

    @transaction.atomic
    def change_company(self, branch: Branch, new_company) -> Branch:
        if new_company.tenant_id != branch.tenant_id:
            raise CompanyMismatchError("New company must belong to the same tenant.")

        branch.company = new_company
        branch.save(update_fields=["company", "updated_at"])

        if hasattr(branch, "settings"):
            branch.settings.company = new_company
            branch.settings.save(update_fields=["company", "updated_at"])

        logger.info("Transferred branch %s to company %s", branch.code, new_company.code)
        return branch
