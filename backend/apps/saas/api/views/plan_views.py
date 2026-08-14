"""REST API ViewSet for SaaS Plans."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.saas.api.serializers import PlanSerializer
from apps.saas.models import Plan


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PlanSerializer
    queryset = Plan.objects.filter(is_active=True, is_public=True).order_by("sort_order")
