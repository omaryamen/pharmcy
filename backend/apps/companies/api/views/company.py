"""Company ViewSet for company CRUD, search, and lifecycle status management."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.companies.permissions import CanManageCompany, CanViewCompany
from apps.companies.selectors import CompanySelector
from apps.companies.serializers import (
    CompanyCloneSerializer,
    CompanyCreateSerializer,
    CompanyDetailSerializer,
    CompanySerializer,
)
from apps.companies.services import CompanyService


@extend_schema_view(
    list=extend_schema(tags=["companies"], summary="List companies for tenant"),
    retrieve=extend_schema(tags=["companies"], summary="Retrieve company details"),
    create=extend_schema(tags=["companies"], summary="Create a new company"),
)
class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = CompanySelector()
        self.company_service = CompanyService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "activate", "deactivate", "suspend", "archive", "restore", "clone"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageCompany)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewCompany)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()
        return self.selector.list_companies(
            tenant=tenant,
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CompanyCreateSerializer
        if self.action == "retrieve":
            return CompanyDetailSerializer
        if self.action == "clone":
            return CompanyCloneSerializer
        return CompanySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = self.company_service.create_company(
            tenant=request.tenant,
            **serializer.validated_data,
        )
        return Response(CompanyDetailSerializer(company).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        company = self.get_object()
        updated = self.company_service.activate_company(company)
        return Response(CompanySerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        company = self.get_object()
        updated = self.company_service.deactivate_company(company)
        return Response(CompanySerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        company = self.get_object()
        updated = self.company_service.suspend_company(company)
        return Response(CompanySerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        company = self.get_object()
        updated = self.company_service.archive_company(company)
        return Response(CompanySerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        company = self.get_object()
        updated = self.company_service.restore_company(company)
        return Response(CompanySerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="clone")
    def clone(self, request, pk=None):
        company = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cloned = self.company_service.clone_company(
            company,
            new_legal_name=serializer.validated_data["new_legal_name"],
            new_code=serializer.validated_data["new_code"],
            new_slug=serializer.validated_data["new_slug"],
        )
        return Response(CompanyDetailSerializer(cloned).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()
        self.company_service.soft_delete_company(company)
        return Response(status=status.HTTP_204_NO_CONTENT)
