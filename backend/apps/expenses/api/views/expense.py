"""REST API ViewSet for Expense CRUD, posting, approval, and reversal."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.branches.models import Branch
from apps.expenses.api.serializers import CreateExpenseSerializer, ExpenseSerializer
from apps.expenses.models import Expense, ExpenseCategory, ExpenseStatus
from apps.expenses.selectors import ExpenseSelector
from apps.expenses.services import ExpenseNumberGenerator, ExpensePostingService, ExpenseReversalService
from apps.companies.models import Company


class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseSerializer
    selector = ExpenseSelector()
    posting_service = ExpensePostingService()
    reversal_service = ExpenseReversalService()
    number_generator = ExpenseNumberGenerator()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_expenses(
            tenant=tenant,
            company_id=self.request.query_params.get("company_id"),
            branch_id=self.request.query_params.get("branch_id"),
            category_id=self.request.query_params.get("category_id"),
            approval_status=self.request.query_params.get("approval_status"),
        )

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = CreateExpenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        company = Company.objects.get(pk=data["company_id"], tenant=tenant)
        branch = Branch.objects.filter(pk=data.get("branch_id"), tenant=tenant).first() if data.get("branch_id") else None
        category = ExpenseCategory.objects.get(pk=data["category_id"], tenant=tenant)

        exp_num = self.number_generator.generate_expense_number(tenant)
        subtotal = data["subtotal"]
        tax = data.get("tax_amount", 0)
        total = subtotal + tax

        expense = Expense.objects.create(
            tenant=tenant,
            company=company,
            branch=branch,
            category=category,
            expense_number=exp_num,
            expense_date=data["expense_date"],
            description=data["description"],
            subtotal=subtotal,
            tax_amount=tax,
            total_amount=total,
            base_total_amount=total,
            payment_method=data.get("payment_method", "cash"),
            approval_status=ExpenseStatus.DRAFT,
            accounting_status="draft",
            created_by=request.user,
        )
        return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        exp = self.get_object()
        exp.approval_status = ExpenseStatus.APPROVED
        exp.approved_by = request.user
        exp.approved_at = request.user.date_joined if hasattr(request.user, "date_joined") else None
        exp.save()
        return Response(ExpenseSerializer(exp).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="post")
    def post_to_gl(self, request: Request, pk: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        exp = self.get_object()

        posted_exp = self.posting_service.post_expense(tenant=tenant, expense=exp, user=request.user)
        return Response(ExpenseSerializer(posted_exp).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request: Request, pk: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        exp = self.get_object()
        reason = request.data.get("reason", "Expense reversed")

        self.reversal_service.reverse_expense(tenant=tenant, expense=exp, reason=reason, user=request.user)
        exp.refresh_from_db()
        return Response(ExpenseSerializer(exp).data, status=status.HTTP_200_OK)
