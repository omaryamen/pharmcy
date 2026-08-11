"""REST API ViewSets for CashRegister and RegisterSession management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.sales.api.serializers import CashRegisterSerializer, RegisterSessionSerializer
from apps.sales.services import PosSalesService


class CashRegisterViewSet(viewsets.ModelViewSet):
    """API endpoints for CashRegister management."""

    serializer_class = CashRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sales_service = PosSalesService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.sales_service.register_repository.get_queryset(tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        reg_num = self.sales_service.number_generator.generate_register_number(tenant)
        serializer.save(tenant=tenant, register_number=reg_num)


class RegisterSessionViewSet(viewsets.ModelViewSet):
    """API endpoints for cashier shift sessions and till cash reconciliation."""

    serializer_class = RegisterSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sales_service = PosSalesService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.sales_service.session_repository.get_queryset(tenant).select_related("cash_register", "cashier")

    @action(detail=False, methods=["post"], url_path="open")
    def open_session(self, request: Request) -> Response:
        """Open a cashier shift session."""
        tenant = getattr(request, "tenant", None)
        register_id = request.data.get("register_id")
        opening_cash = request.data.get("opening_cash", "0.0000")

        reg = self.sales_service.register_repository.get_queryset(tenant).filter(pk=register_id).first()
        if not reg:
            return Response({"detail": "Cash Register not found."}, status=status.HTTP_404_NOT_FOUND)

        session = self.sales_service.open_register_session(tenant, reg, cashier=request.user, opening_cash=opening_cash)
        return Response(self.get_serializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="close")
    def close_session(self, request: Request, pk: str = None) -> Response:
        """Close cashier shift session and calculate till cash variance."""
        tenant = getattr(request, "tenant", None)
        session = self.get_queryset().filter(pk=pk).first()
        if not session:
            return Response({"detail": "Register Session not found."}, status=status.HTTP_404_NOT_FOUND)

        actual_cash = request.data.get("actual_cash", "0.0000")
        notes = request.data.get("notes", "")

        closed = self.sales_service.close_register_session(tenant, session, actual_cash=actual_cash, notes=notes)
        return Response(self.get_serializer(closed).data, status=status.HTTP_200_OK)
