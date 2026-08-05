"""API tests for the RBAC endpoints (roles, groups, assignments, users, me, matrix)."""

from __future__ import annotations

import pytest

from apps.rbac.models import Permission, Role
from tests.factories import RoleFactory, UserFactory

pytestmark = pytest.mark.django_db

API = "/api/v1/rbac"


def _role_id(client, tenant, code: str) -> str:
    response = client.get(f"{API}/roles/")
    assert response.status_code == 200
    for row in response.json()["data"]["results"]:
        if row["code"] == code:
            return row["id"]
    raise AssertionError(f"role '{code}' not found in tenant roles list")


class TestPermissionEndpoints:
    def test_list_permissions(self, rbac_admin_client):
        response = rbac_admin_client.get(f"{API}/permissions/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["count"] == Permission.objects.count()
        assert data["results"]

    def test_retrieve_permission(self, rbac_admin_client):
        permission = Permission.objects.first()
        response = rbac_admin_client.get(f"{API}/permissions/{permission.pk}/")
        assert response.status_code == 200
        assert response.json()["data"]["code"] == permission.code


class TestRoleEndpoints:
    def test_list_roles_contains_bootstrap(self, rbac_admin_client, tenant):
        response = rbac_admin_client.get(f"{API}/roles/")
        assert response.status_code == 200
        codes = {row["code"] for row in response.json()["data"]["results"]}
        assert {"admin", "member"} <= codes

    def test_list_roles_is_tenant_scoped(self, rbac_admin_client, tenant):
        from tests.factories import TenantFactory

        other = TenantFactory()
        RoleFactory(tenant=other, code="foreign_only")
        response = rbac_admin_client.get(f"{API}/roles/")
        codes = {row["code"] for row in response.json()["data"]["results"]}
        assert "foreign_only" not in codes

    def test_create_role(self, rbac_admin_client, tenant):
        response = rbac_admin_client.post(f"{API}/roles/", {"name": "Cashier", "code": "cashier"}, format="json")
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["code"] == "cashier"
        assert data["tenant"] == str(tenant.pk)
        assert data["is_protected"] is False

    def test_create_role_reserved_code_rejected(self, rbac_admin_client):
        response = rbac_admin_client.post(f"{API}/roles/", {"name": "Admin copy", "code": "admin"}, format="json")
        assert response.status_code == 409
        assert response.json()["errors"][0]["code"] == "protected_role"

    def test_role_permissions_matrix(self, rbac_admin_client, tenant):
        admin_id = _role_id(rbac_admin_client, tenant, "admin")
        response = rbac_admin_client.get(f"{API}/roles/{admin_id}/permissions/")
        assert response.status_code == 200
        permissions = response.json()["data"]["permissions"]
        assert "catalog.item.read" in permissions
        assert permissions["catalog.item.read"]["allow"] is True

    def test_replace_role_permissions(self, rbac_admin_client, tenant):
        role_id = _role_id(rbac_admin_client, tenant, "member")
        response = rbac_admin_client.put(
            f"{API}/roles/{role_id}/permissions/",
            {"permissions": {"catalog.item.read": True}},
            format="json",
        )
        assert response.status_code == 200
        permissions = response.json()["data"]["permissions"]
        assert set(permissions) == {"catalog.item.read"}

    def test_set_permissions_rejects_unknown_code(self, rbac_admin_client, tenant):
        role_id = _role_id(rbac_admin_client, tenant, "member")
        response = rbac_admin_client.put(
            f"{API}/roles/{role_id}/permissions/",
            {"permissions": {"no.such.code": True}},
            format="json",
        )
        assert response.status_code == 409

    def test_add_and_remove_parent(self, rbac_admin_client, tenant):
        admin_id = _role_id(rbac_admin_client, tenant, "admin")
        created = rbac_admin_client.post(
            f"{API}/roles/", {"name": "Cashier", "code": "cashier"}, format="json"
        ).json()["data"]
        role_id = created["id"]

        response = rbac_admin_client.post(f"{API}/roles/{role_id}/parents/", {"parent_role": admin_id}, format="json")
        assert response.status_code == 201
        assert response.json()["data"]["parent_code"] == "admin"

        parents = rbac_admin_client.get(f"{API}/roles/{role_id}/parents/")
        assert parents.status_code == 200
        assert parents.json()["data"][0]["parent_code"] == "admin"

        response = rbac_admin_client.delete(f"{API}/roles/{role_id}/parents/{admin_id}/")
        assert response.status_code == 204

    def test_history(self, rbac_admin_client, tenant):
        admin_id = _role_id(rbac_admin_client, tenant, "admin")
        response = rbac_admin_client.get(f"{API}/roles/{admin_id}/history/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["versions"]
        assert data["audit_logs"]

    def test_clone_role(self, rbac_admin_client, tenant):
        admin_id = _role_id(rbac_admin_client, tenant, "admin")
        response = rbac_admin_client.post(
            f"{API}/roles/{admin_id}/clone/",
            {"name": "Admin copy", "code": "admin_copy"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["data"]["code"] == "admin_copy"

    def test_delete_role(self, rbac_admin_client, tenant):
        role_id = _role_id(rbac_admin_client, tenant, "member")
        response = rbac_admin_client.delete(f"{API}/roles/{role_id}/")
        assert response.status_code == 204
        assert not Role.objects.filter(pk=role_id).exists()


class TestGroupEndpoints:
    def test_create_group_and_set_roles(self, rbac_admin_client, tenant):
        response = rbac_admin_client.post(f"{API}/groups/", {"name": "Ops", "code": "ops"}, format="json")
        assert response.status_code == 201
        group_id = response.json()["data"]["id"]

        member_id = _role_id(rbac_admin_client, tenant, "member")
        response = rbac_admin_client.put(f"{API}/groups/{group_id}/roles/", {"role_ids": [member_id]}, format="json")
        assert response.status_code == 200
        assert [row["code"] for row in response.json()["data"]] == ["member"]

        response = rbac_admin_client.get(f"{API}/groups/{group_id}/roles/")
        assert response.status_code == 200

    def test_create_group_duplicate_code_rejected(self, rbac_admin_client):
        rbac_admin_client.post(f"{API}/groups/", {"name": "Ops", "code": "ops"}, format="json")
        response = rbac_admin_client.post(f"{API}/groups/", {"name": "Ops 2", "code": "ops"}, format="json")
        assert response.status_code == 409


class TestAssignmentEndpoints:
    def test_assign_and_revoke(self, rbac_admin_client, tenant):
        target = UserFactory()
        target.tenants.add(tenant)
        cashier = Role.objects.get(tenant=tenant, code="member")

        response = rbac_admin_client.post(
            f"{API}/assignments/",
            {"user": str(target.pk), "role": str(cashier.pk), "reason": "hired"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["data"]["role_code"] == "member"

        assignment_id = response.json()["data"]["id"]
        response = rbac_admin_client.delete(f"{API}/assignments/{assignment_id}/")
        assert response.status_code == 204

    def test_bulk_assign(self, rbac_admin_client, tenant):
        target = UserFactory()
        target.tenants.add(tenant)
        member = Role.objects.get(tenant=tenant, code="member")
        response = rbac_admin_client.post(
            f"{API}/assignments/bulk/",
            {"entries": [{"user": str(target.pk), "role": str(member.pk)}]},
            format="json",
        )
        assert response.status_code == 200
        assert len(response.json()["data"]["assigned"]) == 1


class TestUserEndpoints:
    def test_user_roles(self, rbac_admin_client, tenant):
        target = UserFactory()
        target.tenants.add(tenant)
        admin_id = _role_id(rbac_admin_client, tenant, "admin")

        response = rbac_admin_client.put(
            f"{API}/users/{target.pk}/roles/",
            {"roles": [{"role": admin_id}], "reason": "promote"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["assigned"] == ["admin"]

        response = rbac_admin_client.get(f"{API}/users/{target.pk}/roles/")
        assert response.status_code == 200
        assert [row["role_code"] for row in response.json()["data"]] == ["admin"]

    def test_user_effective_permissions(self, rbac_admin_client, tenant):
        target = UserFactory()
        target.tenants.add(tenant)
        member = Role.objects.get(tenant=tenant, code="member")
        from apps.rbac.services import RoleAssignmentService

        RoleAssignmentService().assign(user=target, role=member, actor=None)

        response = rbac_admin_client.get(f"{API}/users/{target.pk}/permissions/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["count"] > 0
        assert "catalog.item.read" in data["permissions"]

    def test_user_overrides(self, rbac_admin_client, tenant):
        target = UserFactory()
        target.tenants.add(tenant)
        permission = Permission.objects.get(code="catalog.item.read")

        response = rbac_admin_client.post(
            f"{API}/users/{target.pk}/overrides/",
            {"permission": str(permission.pk), "allow": False},
            format="json",
        )
        assert response.status_code == 201
        override_id = response.json()["data"]["id"]
        assert response.json()["data"]["permission_code"] == "catalog.item.read"

        response = rbac_admin_client.get(f"{API}/users/{target.pk}/overrides/")
        assert response.status_code == 200
        assert response.json()["data"]

        response = rbac_admin_client.delete(f"{API}/users/{target.pk}/overrides/{override_id}/")
        assert response.status_code == 204


class TestSelfServiceEndpoints:
    def test_my_permissions(self, rbac_admin_client):
        response = rbac_admin_client.get(f"{API}/me/permissions/")
        assert response.status_code == 200
        data = response.json()["data"]
        tenant_scope_count = Permission.objects.filter(scope="tenant", is_active=True).count()
        assert data["count"] == tenant_scope_count
        assert "catalog" in data["modules"]
        assert data["roles"]

    def test_my_navigation(self, rbac_admin_client):
        response = rbac_admin_client.get(f"{API}/me/navigation/")
        assert response.status_code == 200
        navigation = response.json()["data"]["navigation"]
        assert navigation
        modules = {item["module"] for item in navigation}
        assert "catalog" in modules
        assert "platform" not in modules

    def test_member_can_read_own_permissions(self, tenant_authenticated_client, tenant):
        response = tenant_authenticated_client.get(f"{API}/me/permissions/")
        assert response.status_code == 200
        assert response.json()["data"]["count"] >= 1

    def test_member_can_read_own_navigation(self, tenant_authenticated_client):
        response = tenant_authenticated_client.get(f"{API}/me/navigation/")
        assert response.status_code == 200


class TestMatrixEndpoint:
    def test_caller_matrix(self, rbac_admin_client):
        response = rbac_admin_client.get(f"{API}/matrix/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["count"] == Permission.objects.filter(is_active=True).count()
        assert data["granted_count"] == Permission.objects.filter(scope="tenant", is_active=True).count()
        assert data["permissions"]["catalog.item.read"]["granted"] is True

    def test_role_matrix(self, rbac_admin_client, tenant):
        admin_id = _role_id(rbac_admin_client, tenant, "admin")
        response = rbac_admin_client.get(f"{API}/matrix/?role={admin_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["code"] == "admin"
        assert data["matrix"]["catalog.item.read"]["allow"] is True


class TestAuthorization:
    def test_anonymous_rejected(self, api_client):
        response = api_client.get(f"{API}/roles/")
        assert response.status_code == 401

    def test_member_without_rbac_permissions_rejected(self, tenant_authenticated_client):
        response = tenant_authenticated_client.get(f"{API}/roles/")
        assert response.status_code == 403

    def test_member_cannot_create_roles(self, tenant_authenticated_client):
        response = tenant_authenticated_client.post(
            f"{API}/roles/", {"name": "Cashier", "code": "cashier"}, format="json"
        )
        assert response.status_code == 403
