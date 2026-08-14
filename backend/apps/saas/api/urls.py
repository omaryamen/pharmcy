"""URL Routing Configuration for SaaS Subscription, Billing & Licensing REST API."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.saas.api.views import (
    PlanViewSet,

    SaaSAnalyticsView,
    SubscriptionViewSet,
)

router = DefaultRouter()
router.register(r"saas/plans", PlanViewSet, basename="saas-plans")
router.register(r"saas/subscriptions", SubscriptionViewSet, basename="saas-subscriptions")

urlpatterns = router.urls + [
    path("saas/analytics/", SaaSAnalyticsView.as_view(), name="saas-analytics"),
]
