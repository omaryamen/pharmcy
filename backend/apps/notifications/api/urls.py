"""URL Routing Configuration for Enterprise Notifications REST API."""

from rest_framework.routers import DefaultRouter

from apps.notifications.api.views import (
    NotificationPreferenceViewSet,
    NotificationViewSet,
)

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notifications")
router.register(r"notification-preferences", NotificationPreferenceViewSet, basename="notification-preferences")

urlpatterns = router.urls
