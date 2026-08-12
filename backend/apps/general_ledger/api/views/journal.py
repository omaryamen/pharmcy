"""REST API ViewSet for JournalEntry posting and reversals."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.general_ledger.api.serializers import (
    CreateManualJournalSerializer,
    JournalEntrySerializer,
    ReverseJournalSerializer,
)
from apps.general_ledger.selectors import GLSelector
from apps.general_ledger.services import JournalPostingService, JournalReversalService


class JournalEntryViewSet(viewsets.ModelViewSet):
    """ViewSet managing double-entry journal postings, queries, and immutable reversals."""

    permission_classes = [IsAuthenticated]
    serializer_class = JournalEntrySerializer
    selector = GLSelector()
    posting_service = JournalPostingService()
    reversal_service = JournalReversalService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_journals(
            tenant=tenant,
            company_id=self.request.query_params.get("company_id"),
            status=self.request.query_params.get("status"),
            reference_type=self.request.query_params.get("reference_type"),
            source_module=self.request.query_params.get("source_module"),
            search=self.request.query_params.get("search"),
        )

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = CreateManualJournalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        company = Company.objects.get(pk=data["company_id"], tenant=tenant)
        branch = Branch.objects.get(pk=data["branch_id"], tenant=tenant) if data.get("branch_id") else None

        lines_input = []
        for line in data["lines"]:
            lines_input.append({
                "account": str(line["account_id"]),
                "debit": line["debit"],
                "credit": line["credit"],
                "description": line.get("description", ""),
            })

        journal = self.posting_service.create_and_post_journal_entry(
            tenant=tenant,
            company=company,
            branch=branch,
            posting_date=data["posting_date"],
            description=data["description"],
            lines_data=lines_input,
            reference_type="MANUAL_JOURNAL",
            source_module="general_ledger",
            user=request.user,
        )
        return Response(JournalEntrySerializer(journal).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request: Request, pk: str = None) -> Response:
        serializer = ReverseJournalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = getattr(request.user, "tenant", None)
        jrn = self.get_object()

        reversal_jrn = self.reversal_service.reverse_journal_entry(
            tenant=tenant,
            journal_entry=jrn,
            reversal_reason=serializer.validated_data["reversal_reason"],
            user=request.user,
        )
        return Response(JournalEntrySerializer(reversal_jrn).data, status=status.HTTP_200_OK)
