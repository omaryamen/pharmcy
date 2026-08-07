"""Tenant ViewSet for tenant lifecycle operations and provisioning."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAuthenticatedAndActive
from apps.tenants.permissions import IsPlatformAdmin, IsTenantOwner
from apps.tenants.selectors import TenantSelector
from apps.tenants.serializers import (
    TenantCloneSerializer,
    TenantCreateSerializer,
    TenantDetailSerializer,
    TenantSerializer,
    TenantTransferOwnershipSerializer,
)
from apps.tenants.services import TenantLifecycleService, TenantProvisioningService

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=["tenants"], summary="List all tenants"),
    retrieve=extend_schema(tags=["tenants"], summary="Retrieve tenant details"),
    create=extend_schema(tags=["tenants"], summary="Provision a new tenant"),
)
class TenantViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = TenantSelector()
        self.provisioning_service = TenantProvisioningService()
        self.lifecycle_service = TenantLifecycleService()

    def get_permissions(self):
        if self.action in {"list", "create", "archive", "restore"}:
            return [IsPlatformAdmin()]
        if self.action in {"activate", "suspend", "deactivate", "transfer_ownership", "clone", "destroy"}:
            return [(IsPlatformAdmin | IsTenantOwner)()]
        return [IsAuthenticatedAndActive()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return self.selector.list_tenants(
                status=self.request.query_params.get("status"),
                search=self.request.query_params.get("search"),
            )
        return user.tenants.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action == "create":
            return TenantCreateSerializer
        if self.action == "retrieve":
            return TenantDetailSerializer
        if self.action == "transfer_ownership":
            return TenantTransferOwnershipSerializer
        if self.action == "clone":
            return TenantCloneSerializer
        return TenantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = self.provisioning_service.provision_tenant(
            owner_id=getattr(request.user, "pk", None),
            **serializer.validated_data,
        )
        return Response(TenantDetailSerializer(tenant).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return Response({"detail": "No tenant context resolved for current request."}, status=status.HTTP_404_NOT_FOUND)
        return Response(TenantDetailSerializer(tenant).data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        tenant = self.get_object()
        updated = self.lifecycle_service.activate_tenant(tenant)
        return Response(TenantSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        tenant = self.get_object()
        updated = self.lifecycle_service.suspend_tenant(tenant)
        return Response(TenantSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        tenant = self.get_object()
        updated = self.lifecycle_service.deactivate_tenant(tenant)
        return Response(TenantSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        tenant = self.get_object()
        updated = self.lifecycle_service.archive_tenant(tenant)
        return Response(TenantSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        tenant = self.get_object()
        updated = self.lifecycle_service.restore_tenant(tenant)
        return Response(TenantSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="transfer-ownership")
    def transfer_ownership(self, request, pk=None):
        tenant = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_owner = User.objects.get(pk=serializer.validated_data["new_owner_id"])
        updated = self.lifecycle_service.transfer_ownership(tenant, new_owner)
        return Response(TenantSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="clone")
    def clone(self, request, pk=None):
        source_tenant = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_owner = User.objects.filter(pk=serializer.validated_data.get("new_owner_id")).first() or request.user
        cloned = self.lifecycle_service.clone_tenant(
            source_tenant,
            new_name=serializer.validated_data["new_name"],
            new_slug=serializer.validated_data["new_slug"],
            new_code=serializer.validated_data.get("new_code"),
            new_owner=new_owner,
        )
        return Response(TenantDetailSerializer(cloned).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        tenant = self.get_object()
        self.lifecycle_service.soft_delete_tenant(tenant)
        return Response(status=status.HTTP_204_NO_CONTENT)
