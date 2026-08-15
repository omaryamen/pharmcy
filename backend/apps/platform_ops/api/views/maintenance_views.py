"""REST API ViewSet for System Maintenance Windows."""

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from apps.platform_ops.api.serializers import SystemMaintenanceWindowSerializer
from apps.platform_ops.models import SystemMaintenanceWindow


class SystemMaintenanceWindowViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = SystemMaintenanceWindowSerializer
    queryset = SystemMaintenanceWindow.objects.all().order_by("-start_time")
