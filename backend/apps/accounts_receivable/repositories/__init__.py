"""Export repositories for apps.accounts_receivable."""

from apps.accounts_receivable.repositories.receivable_repository import (
    CustomerPaymentRepository,
    CustomerReceivableRepository,
)

__all__ = [
    "CustomerReceivableRepository",
    "CustomerPaymentRepository",
]
