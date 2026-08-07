"""Branch Settings ViewSet."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.branches.permissions import CanManageBranch, CanViewBranch
from apps.branches.repositories import BranchRepository, BranchSettingsRepository
from apps.branches.serializers import BranchSettingsSerializer
from apps.branches.services import BranchSettingsService


class BranchSettingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]
    serializer_class = BranchSettingsSerializer

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.branch_repository = BranchRepository()
        self.settings_repository = BranchSettingsRepository()
        self.settings_service = BranchSettingsService()

    def get_permissions(self):
        if self.action in {"partial_update", "update"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageBranch)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewBranch)()]

    @extend_schema(tags=["branches"], summary="Retrieve branch settings")
    def retrieve(self, request, branch_id=None):
        branch = self.branch_repository.get_or_none(tenant=request.tenant, pk=branch_id)
        if not branch:
            return Response({"detail": "Branch not found."}, status=status.HTTP_404_NOT_FOUND)
        settings_obj, _ = self.settings_repository.get_or_create(
            branch=branch,
            defaults={"company": branch.company, "tenant": request.tenant},
        )
        return Response(BranchSettingsSerializer(settings_obj).data)

    @extend_schema(tags=["branches"], summary="Update branch settings")
    def partial_update(self, request, branch_id=None):
        branch = self.branch_repository.get_or_none(tenant=request.tenant, pk=branch_id)
        if not branch:
            return Response({"detail": "Branch not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BranchSettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = self.settings_service.update_settings(branch, **serializer.validated_data)
        return Response(BranchSettingsSerializer(updated).data)
