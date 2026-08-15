"""REST API ViewSet for Global Feature Flags."""

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from apps.platform_ops.api.serializers import GlobalFeatureFlagSerializer
from apps.platform_ops.models import GlobalFeatureFlag


class GlobalFeatureFlagViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = GlobalFeatureFlagSerializer
    queryset = GlobalFeatureFlag.objects.all().order_by("feature_key")
