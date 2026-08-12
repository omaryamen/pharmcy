"""REST API ViewSet for ChartOfAccount management."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.companies.models import Company
from apps.general_ledger.api.serializers import ChartOfAccountSerializer
from apps.general_ledger.selectors import GLSelector
from apps.general_ledger.services import ChartOfAccountsService


class ChartOfAccountViewSet(viewsets.ModelViewSet):
    """ViewSet managing Chart of Accounts setup and default seeding."""

    permission_classes = [IsAuthenticated]
    serializer_class = ChartOfAccountSerializer
    selector = GLSelector()
    coa_service = ChartOfAccountsService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_accounts(
            tenant=tenant,
            company_id=self.request.query_params.get("company_id"),
            account_type=self.request.query_params.get("account_type"),
            search=self.request.query_params.get("search"),
        )

    @action(detail=False, methods=["post"], url_path="seed-defaults")
    def seed_defaults(self, request: Request) -> Response:
        company_id = request.data.get("company_id")
        tenant = getattr(request.user, "tenant", None)
        company = Company.objects.get(pk=company_id, tenant=tenant)

        seeded_map = self.coa_service.seed_default_chart_of_accounts(tenant, company)
        return Response(
            {"message": f"Successfully seeded {len(seeded_map)} default accounts for company {company.legal_name}."},
            status=status.HTTP_201_CREATED,
        )
