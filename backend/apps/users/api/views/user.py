"""User ViewSet for Enterprise User Management."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.branches.repositories import BranchRepository
from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.companies.repositories import CompanyRepository
from apps.rbac.repositories import RoleRepository
from apps.users.permissions import CanManageUsers, CanViewUsers
from apps.users.selectors import UserSelector
from apps.users.serializers import (
    UserAssignBranchSerializer,
    UserAssignRoleSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserResetPasswordSerializer,
    UserSerializer,
)
from apps.users.services import UserService


@extend_schema_view(
    list=extend_schema(tags=["users"], summary="List users for tenant"),
    retrieve=extend_schema(tags=["users"], summary="Retrieve user details"),
    create=extend_schema(tags=["users"], summary="Create a new enterprise user"),
)
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = UserSelector()
        self.user_service = UserService()
        self.company_repository = CompanyRepository()
        self.branch_repository = BranchRepository()
        self.role_repository = RoleRepository()

    def get_permissions(self):
        if self.action == "me":
            return [IsAuthenticatedAndActive()]
        if self.action in {"create", "update", "partial_update", "destroy", "activate", "deactivate", "lock", "unlock", "reset_password", "assign_role", "revoke_role", "assign_branch"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageUsers)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewUsers)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.user_repository.model.objects.none()

        return self.selector.list_users(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "retrieve":
            return UserDetailSerializer
        if self.action == "assign_role":
            return UserAssignRoleSerializer
        if self.action == "assign_branch":
            return UserAssignBranchSerializer
        if self.action == "reset_password":
            return UserResetPasswordSerializer
        return UserSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["tenant"] = getattr(self.request, "tenant", None)
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        company = self.company_repository.get_or_none(tenant=request.tenant, pk=data["company_id"])
        if not company:
            return Response({"detail": "Specified company not found in this tenant."}, status=status.HTTP_404_NOT_FOUND)

        primary_branch = None
        if data.get("primary_branch_id"):
            primary_branch = self.branch_repository.get_or_none(tenant=request.tenant, pk=data["primary_branch_id"])

        branch_objs = []
        if data.get("branch_ids"):
            branch_objs = list(self.branch_repository.filter(tenant=request.tenant, pk__in=data["branch_ids"]))

        role_objs = []
        if data.get("role_ids"):
            role_objs = list(self.role_repository.filter(tenant=request.tenant, pk__in=data["role_ids"]))

        user = self.user_service.create_enterprise_user(
            tenant=request.tenant,
            company=company,
            primary_branch=primary_branch,
            email=data["email"],
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            username=data.get("username"),
            password=data.get("password"),
            phone=data.get("phone", ""),
            employee_number=data.get("employee_number", ""),
            arabic_name=data.get("arabic_name", ""),
            english_name=data.get("english_name", ""),
            job_title=data.get("job_title", ""),
            department=data.get("department", ""),
            roles=role_objs,
            branches=branch_objs,
        )

        return Response(UserDetailSerializer(user, context={"tenant": request.tenant}).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        user = self.selector.get_user_detail(request.tenant, request.user.pk) if getattr(request, "tenant", None) else request.user
        return Response(UserDetailSerializer(user or request.user, context={"tenant": getattr(request, "tenant", None)}).data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        user = self.get_object()
        updated = self.user_service.activate_user(user)
        return Response(UserSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        user = self.get_object()
        updated = self.user_service.deactivate_user(user)
        return Response(UserSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="lock")
    def lock(self, request, pk=None):
        user = self.get_object()
        updated = self.user_service.lock_user(user)
        return Response(UserSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="unlock")
    def unlock(self, request, pk=None):
        user = self.get_object()
        updated = self.user_service.unlock_user(user)
        return Response(UserSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.user_service.reset_password(user, serializer.validated_data["new_password"])
        return Response({"detail": "Password successfully reset."})

    @action(detail=True, methods=["post"], url_path="assign-role")
    def assign_role(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = self.role_repository.get_or_none(tenant=request.tenant, pk=serializer.validated_data["role_id"])
        if not role:
            return Response({"detail": "Specified role not found in this tenant."}, status=status.HTTP_404_NOT_FOUND)

        self.user_service.assign_role(user, role, request.tenant)
        return Response(UserDetailSerializer(user, context={"tenant": request.tenant}).data)

    @action(detail=True, methods=["post"], url_path="revoke-role")
    def revoke_role(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = self.role_repository.get_or_none(tenant=request.tenant, pk=serializer.validated_data["role_id"])
        if not role:
            return Response({"detail": "Specified role not found in this tenant."}, status=status.HTTP_404_NOT_FOUND)

        self.user_service.revoke_role(user, role, request.tenant)
        return Response(UserDetailSerializer(user, context={"tenant": request.tenant}).data)

    @action(detail=True, methods=["post"], url_path="assign-branch")
    def assign_branch(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        branch = self.branch_repository.get_or_none(tenant=request.tenant, pk=serializer.validated_data["branch_id"])
        if not branch:
            return Response({"detail": "Specified branch not found in this tenant."}, status=status.HTTP_404_NOT_FOUND)

        if serializer.validated_data.get("is_primary"):
            self.user_service.transfer_primary_branch(user, branch)
        else:
            self.user_service.assign_branch(user, branch)

        return Response(UserDetailSerializer(user, context={"tenant": request.tenant}).data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        self.user_service.soft_delete_user(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
