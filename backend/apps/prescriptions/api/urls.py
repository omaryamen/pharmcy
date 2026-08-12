"""URL Routing Configuration for Enterprise Prescription Management REST API."""

from rest_framework.routers import DefaultRouter

from apps.prescriptions.api.views import PrescriptionDispenseViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r"prescriptions", PrescriptionViewSet, basename="prescription")
router.register(r"dispensations", PrescriptionDispenseViewSet, basename="dispensation")

urlpatterns = router.urls
