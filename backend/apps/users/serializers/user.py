"""User serializers for Enterprise User Management."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.serializers.profile import EmployeeProfileSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    employee_profile = EmployeeProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "avatar",
            "language",
            "timezone",
            "status",
            "is_active",
            "is_staff",
            "is_superuser",
            "email_verified",
            "phone_verified",
            "employee_profile",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    username = serializers.CharField(max_length=150, required=False, allow_null=True, default=None)
    password = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")

    company_id = serializers.UUIDField()
    primary_branch_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    branch_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    role_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)

    employee_number = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    arabic_name = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    english_name = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    job_title = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    department = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")


class UserDetailSerializer(UserSerializer):
    roles = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["roles"]

    def get_roles(self, obj) -> list[dict]:
        tenant = self.context.get("tenant")
        assignments = getattr(obj, "role_assignments", None)
        if assignments is not None:
            return [
                {"id": str(ra.role.id), "name": ra.role.name, "code": ra.role.code}
                for ra in assignments.all()
                if not tenant or ra.tenant_id == tenant.pk
            ]
        return []


class UserAssignRoleSerializer(serializers.Serializer):
    role_id = serializers.UUIDField()


class UserAssignBranchSerializer(serializers.Serializer):
    branch_id = serializers.UUIDField()
    is_primary = serializers.BooleanField(default=False)


class UserResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8)
