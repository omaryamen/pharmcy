"""REST API View for Customer Mobile Home Screen Dashboard."""

from rest_framework import permissions, status, views
from rest_framework.request import Request
from rest_framework.response import Response

from apps.customers.models import Customer
from apps.mobile_api.selectors import CustomerDashboardSelector


class CustomerMobileDashboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    selector = CustomerDashboardSelector()

    def get(self, request: Request) -> Response:
        customer_id = request.query_params.get("customer_id")
        customer = None
        if customer_id:
            customer = Customer.objects.filter(pk=customer_id).first()
        elif hasattr(request.user, "customer_profile"):
            customer = request.user.customer_profile

        if not customer:
            return Response({"error": "Valid customer context required."}, status=status.HTTP_400_BAD_REQUEST)

        dashboard = self.selector.get_customer_dashboard(customer)
        return Response(dashboard, status=status.HTTP_200_OK)
