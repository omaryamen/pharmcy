"""RBAC API serializers.

Read serializers reflect model state; write serializers feed the services,
which remain the single authority for business rules and transactions.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    Permission,
    Role,
    RoleAuditLog,
    RoleGroup,
    RoleHierarchy,
    RolePermission,
    RoleVersion,
    UserPermissionOverride,
    UserRoleAssignment,
)


# ---------------------------------------------------------------------------
# Permission catalog
# ---------------------------------------------------------------------------
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            "id",
            "code",
            "name",
            "description",
            "module",
            "category",
            "action",
            "scope",
            "is_system",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "is_system", "created_at", "updated_at")


class PermissionWriteSerializer(PermissionSerializer):
    class Meta(PermissionSerializer.Meta):
        read_only_fields = ("id", "is_system", "created_at", "updated_at")


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
class RoleSerializer(serializers.ModelSerializer):
    permission_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()
    parent_codes = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            "id",
            "tenant",
            "name",
            "code",
            "description",
            "is_protected",
            "is_default",
            "is_active",
            "permission_count",
            "user_count",
            "parent_codes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "tenant", "is_protected", "permission_count", "user_count", "parent_codes")

    def get_permission_count(self, obj) -> int:
        return obj.permission_links.count()

    def get_user_count(self, obj) -> int:
        return obj.assignments.filter(is_active=True).count()

    def get_parent_codes(self, obj) -> list[str]:
        return list(obj.parent_links.values_list("parent_role__code", flat=True))


class RoleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "code", "description", "is_protected", "is_default", "is_active")
        read_only_fields = ("id", "is_protected")


class RolePermissionSerializer(serializers.ModelSerializer):
    permission_code = serializers.CharField(source="permission.code", read_only=True)
    permission_name = serializers.CharField(source="permission.name", read_only=True)
    permission_module = serializers.CharField(source="permission.module", read_only=True)

    class Meta:
        model = RolePermission
        fields = ("id", "role", "permission", "permission_code", "permission_name", "permission_module", "allow")


class RolePermissionMapSerializer(serializers.Serializer):
    """Replace a role's permission set: ``{"permissions": {"code": bool}}``."""

    permissions = serializers.DictField(child=serializers.BooleanField(), required=True)


class RoleCloneSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=True)
    code = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------
class RoleHierarchySerializer(serializers.ModelSerializer):
    parent_code = serializers.CharField(source="parent_role.code", read_only=True)
    parent_name = serializers.CharField(source="parent_role.name", read_only=True)

    class Meta:
        model = RoleHierarchy
        fields = ("id", "child_role", "parent_role", "parent_code", "parent_name", "created_at")
        read_only_fields = ("id", "child_role", "parent_code", "parent_name", "created_at")


class RoleParentLinkSerializer(serializers.Serializer):
    parent_role = serializers.UUIDField(required=True)


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------
class RoleGroupSerializer(serializers.ModelSerializer):
    role_count = serializers.SerializerMethodField()

    class Meta:
        model = RoleGroup
        fields = ("id", "tenant", "name", "code", "description", "is_active", "role_count", "created_at", "updated_at")
        read_only_fields = ("id", "tenant", "role_count")

    def get_role_count(self, obj) -> int:
        return obj.memberships.count()


class RoleGroupRolesSerializer(serializers.Serializer):
    role_ids = serializers.ListField(child=serializers.UUIDField(), required=True)


# ---------------------------------------------------------------------------
# Assignments
# ---------------------------------------------------------------------------
class RoleAssignmentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    role_code = serializers.CharField(source="role.code", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = UserRoleAssignment
        fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "role",
            "role_code",
            "role_name",
            "is_primary",
            "is_active",
            "reason",
            "created_at",
        )
        read_only_fields = ("id", "user_email", "user_name", "role_code", "role_name", "created_at")


class RoleAssignSerializer(serializers.Serializer):
    role = serializers.UUIDField(required=True)
    is_primary = serializers.BooleanField(required=False, default=False)
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class AssignmentCreateSerializer(serializers.Serializer):
    user = serializers.UUIDField(required=True)
    role = serializers.UUIDField(required=True)
    is_primary = serializers.BooleanField(required=False, default=False)
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class UserRolesReplaceSerializer(serializers.Serializer):
    roles = RoleAssignSerializer(many=True, required=True)
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class BulkAssignEntrySerializer(serializers.Serializer):
    user = serializers.UUIDField(required=True)
    role = serializers.UUIDField(required=True)
    is_primary = serializers.BooleanField(required=False, default=False)
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class BulkAssignSerializer(serializers.Serializer):
    entries = BulkAssignEntrySerializer(many=True, required=True)


class UserPermissionOverrideSerializer(serializers.ModelSerializer):
    permission_code = serializers.CharField(source="permission.code", read_only=True)
    permission_name = serializers.CharField(source="permission.name", read_only=True)

    class Meta:
        model = UserPermissionOverride
        fields = (
            "id",
            "user",
            "user_email",
            "permission",
            "permission_code",
            "permission_name",
            "allow",
            "created_at",
        )
        read_only_fields = ("id", "permission_code", "permission_name", "created_at")

    user_email = serializers.CharField(source="user.email", read_only=True)


# ---------------------------------------------------------------------------
# History / audit
# ---------------------------------------------------------------------------
class RoleVersionSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True, allow_null=True)

    class Meta:
        model = RoleVersion
        fields = ("version", "snapshot", "reason", "created_by_email", "created_at")
        read_only_fields = fields


class RoleAuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)

    class Meta:
        model = RoleAuditLog
        fields = ("action", "actor_email", "details", "created_at")
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Read-side payloads (schema/documentation)
# ---------------------------------------------------------------------------
class PermissionInfoSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    module = serializers.CharField()
    category = serializers.CharField()
    action = serializers.CharField()
    scope = serializers.CharField()


class EffectivePermissionsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    permissions = serializers.DictField(child=PermissionInfoSerializer())
    modules = serializers.ListField(child=serializers.CharField())


class NavigationItemSerializer(serializers.Serializer):
    module = serializers.CharField()
    label = serializers.CharField()
    icon = serializers.CharField()
    route = serializers.CharField()
    order = serializers.IntegerField()
    permissions = serializers.ListField(child=serializers.CharField())
