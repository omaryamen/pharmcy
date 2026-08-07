"""Branch ViewSet for CRUD, search, status lifecycle, manager assignment, and company transfer."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.branches.permissions import CanManageBranch, CanViewBranch
from apps.branches.selectors import BranchSelector
from apps.branches.serializers import (
    BranchAssignManagerSerializer,
    BranchChangeCompanySerializer,
    BranchCreateSerializer,
    BranchDetailSerializer,
    BranchSerializer,
)
from apps.branches.services import BranchService
from apps.companies.repositories import CompanyRepository

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=["branches"], summary="List branches for tenant & company"),
    retrieve=extend_schema(tags=["branches"], summary="Retrieve branch details"),
    create=extend_schema(tags=["branches"], summary="Create a new branch"),
)
class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = BranchSelector()
        self.branch_service = BranchService()
        self.company_repository = CompanyRepository()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "activate", "deactivate", "suspend", "archive", "restore", "assign_manager", "change_company"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageBranch)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewBranch)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        return self.selector.list_branches(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            status=self.request.query_params.get("status"),
            branch_type=self.request.query_params.get("branch_type"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return BranchCreateSerializer
        if self.action == "retrieve":
            return BranchDetailSerializer
        if self.action == "assign_manager":
            return BranchAssignManagerSerializer
        if self.action == "change_company":
            return BranchChangeCompanySerializer
        return BranchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = serializer.validated_data.pop("company")
        branch = self.branch_service.create_branch(
            tenant=request.tenant,
            company=company,
            **serializer.validated_data,
        )
        return Response(BranchDetailSerializer(branch).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        branch = self.get_object()
        updated = self.branch_service.activate_branch(branch)
        return Response(BranchSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        branch = self.get_object()
        updated = self.branch_service.deactivate_branch(branch)
        return Response(BranchSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        branch = self.get_object()
        updated = self.branch_service.suspend_branch(branch)
        return Response(BranchSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        branch = self.get_object()
        updated = self.branch_service.archive_branch(branch)
        return Response(BranchSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        branch = self.get_object()
        updated = self.branch_service.restore_branch(branch)
        return Response(BranchSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="assign-manager")
    def assign_manager(self, request, pk=None):
        branch = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager_user = User.objects.filter(pk=serializer.validated_data["manager_id"]).first()
        if not manager_user:
            return Response({"detail": "Specified manager user not found."}, status=status.HTTP_404_NOT_FOUND)

        updated = self.branch_service.assign_manager(branch, manager_user)
        return Response(BranchSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="change-company")
    def change_company(self, request, pk=None):
        branch = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_company = self.company_repository.get_or_none(tenant=request.tenant, pk=serializer.validated_data["new_company_id"])
        if not new_company:
            return Response({"detail": "Specified company not found in this tenant."}, status=status.HTTP_404_NOT_FOUND)

        updated = self.branch_service.change_company(branch, new_company)
        return Response(BranchSerializer(updated).data)

    def destroy(self, request, *args, **kwargs):
        branch = self.get_object()
        self.branch_service.soft_delete_branch(branch)
        return Response(status=status.HTTP_204_NO_CONTENT)
