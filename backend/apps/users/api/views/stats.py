"""User Statistics View."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.users.permissions import CanViewUsers
from apps.users.selectors import UserSelector


class UserStatsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewUsers]

    @extend_schema(tags=["users"], summary="Retrieve enterprise user statistics")
    def get(self, request):
        stats = UserSelector().get_user_stats(request.tenant)
        return Response(stats)
