"""REST API ViewSet for Prescription document management."""

from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.customers.models import Customer
from apps.prescriptions.api.serializers import (
    DispensePrescriptionCreateSerializer,
    PrescriptionCreateSerializer,
    PrescriptionDispenseSerializer,
    PrescriptionSerializer,
)
from apps.prescriptions.models import Prescription
from apps.prescriptions.selectors import PrescriptionSelector
from apps.prescriptions.services import PharmacyDispensingService
from apps.warehouses.models import Warehouse


class PrescriptionViewSet(viewsets.ModelViewSet):
    """ViewSet managing Prescription creation, verification, dispensing, and statistics."""

    permission_classes = [IsAuthenticated]
    serializer_class = PrescriptionSerializer
    selector = PrescriptionSelector()
    service = PharmacyDispensingService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_prescriptions(
            tenant=tenant,
            search=self.request.query_params.get("search"),
            status=self.request.query_params.get("status"),
            rx_type=self.request.query_params.get("rx_type"),
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = PrescriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        company = Company.objects.get(pk=data["company_id"], tenant=tenant)
        branch = Branch.objects.get(pk=data["branch_id"], tenant=tenant)
        customer = Customer.objects.get(pk=data["customer_id"], tenant=tenant)

        prescription = self.service.create_prescription(
            tenant=tenant,
            company=company,
            branch=branch,
            customer=customer,
            rx_date=data["rx_date"],
            expiry_date=data["expiry_date"],
            doctor_name=data["doctor_name"],
            lines_data=data["lines"],
            rx_type=data.get("rx_type", "regular"),
            doctor_license_number=data.get("doctor_license_number", ""),
            clinic_hospital_name=data.get("clinic_hospital_name", ""),
            diagnosis_code=data.get("diagnosis_code", ""),
            diagnosis_description=data.get("diagnosis_description", ""),
            notes=data.get("notes", ""),
            idempotency_key=data.get("idempotency_key", ""),
            user=request.user,
        )
        return Response(PrescriptionSerializer(prescription).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request: Request, pk: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        rx = self.get_object()
        verified_rx = self.service.verify_prescription(tenant, rx, pharmacist=request.user)
        return Response(PrescriptionSerializer(verified_rx).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="dispense")
    def dispense(self, request: Request, pk: str = None) -> Response:
        serializer = DispensePrescriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        rx = self.get_object()
        warehouse = Warehouse.objects.get(pk=data["warehouse_id"], tenant=tenant)

        dispense = self.service.dispense_prescription(
            tenant=tenant,
            prescription=rx,
            warehouse=warehouse,
            dispensing_lines=data["dispensing_lines"],
            pharmacist=request.user,
            pharmacist_notes=data.get("pharmacist_notes", ""),
        )
        return Response(PrescriptionDispenseSerializer(dispense).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        stats = self.selector.get_dispensing_statistics(tenant=tenant)
        return Response(stats, status=status.HTTP_200_OK)
