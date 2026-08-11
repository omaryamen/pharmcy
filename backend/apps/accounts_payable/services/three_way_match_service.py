"""Three-Way Matching Engine service for Purchase Order, Goods Receipt, and Supplier Invoice verification."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction

from apps.accounts_payable.models import MatchStatus, SupplierInvoice

logger = logging.getLogger(__name__)


class ThreeWayMatchService:
    """Performs strict three-way verification across Purchase Orders, Goods Receipts, and Supplier Invoices."""

    @transaction.atomic
    def verify_and_match_invoice(self, tenant: Any, invoice: SupplierInvoice, user: Any | None = None) -> MatchStatus:
        """Perform line-by-line 3-way match validation."""
        po = invoice.purchase_order
        grn = invoice.goods_receipt

        # 1. Supplier Mismatch Check
        if po and po.supplier_id != invoice.supplier_id:
            logger.warning("Supplier mismatch: Invoice %s supplier (%s) != PO supplier (%s)", invoice.invoice_number, invoice.supplier_id, po.supplier_id)
            invoice.match_status = MatchStatus.SUPPLIER_MISMATCH
            invoice.save(update_fields=["match_status", "updated_at"])
            return MatchStatus.SUPPLIER_MISMATCH

        if grn and grn.supplier_id != invoice.supplier_id:
            logger.warning("Supplier mismatch: Invoice %s supplier (%s) != GRN supplier (%s)", invoice.invoice_number, invoice.supplier_id, grn.supplier_id)
            invoice.match_status = MatchStatus.SUPPLIER_MISMATCH
            invoice.save(update_fields=["match_status", "updated_at"])
            return MatchStatus.SUPPLIER_MISMATCH

        # 2. Receipt Missing Check
        if po and not grn and invoice.lines.filter(goods_receipt_line__isnull=True).exists():
            # If PO exists but zero physical goods receipt is linked or recorded
            if not po.lines.filter(received_quantity__gt=Decimal("0")).exists():
                logger.warning("Goods Receipt missing for invoice %s linked to PO %s", invoice.invoice_number, po.po_number)
                invoice.match_status = MatchStatus.RECEIPT_MISSING
                invoice.save(update_fields=["match_status", "updated_at"])
                return MatchStatus.RECEIPT_MISSING

        # 3. Line-by-Line Quantity & Price Variance Checks
        detected_status = MatchStatus.MATCHED

        for line in invoice.lines.select_related("purchase_order_line", "goods_receipt_line"):
            po_line = line.purchase_order_line
            grn_line = line.goods_receipt_line

            # Check Quantity Variance against Goods Receipt
            rec_qty = Decimal("0.0000")
            if grn_line:
                rec_qty = grn_line.accepted_quantity
            elif po_line:
                rec_qty = po_line.received_quantity

            line.received_quantity = rec_qty
            line.save(update_fields=["received_quantity"])

            if line.quantity > rec_qty and rec_qty < Decimal("0.0001"):
                detected_status = MatchStatus.RECEIPT_MISSING
                break
            elif line.quantity > rec_qty:
                logger.warning("Quantity variance detected for line %s: Invoiced (%s) > Received (%s)", line.pk, line.quantity, rec_qty)
                detected_status = MatchStatus.QUANTITY_VARIANCE
                break

            # Check Price Variance against Purchase Order
            if po_line:
                if line.unit_price != po_line.unit_price:
                    logger.warning("Price variance detected for line %s: Invoiced (%s) != PO Price (%s)", line.pk, line.unit_price, po_line.unit_price)
                    detected_status = MatchStatus.PRICE_VARIANCE
                    break

        invoice.match_status = detected_status
        invoice.save(update_fields=["match_status", "updated_at"])

        logger.info("Three-way match result for invoice %s: %s", invoice.invoice_number, detected_status)
        return detected_status
