"""Export repositories for apps.sales_returns."""

from apps.sales_returns.repositories.returns_repository import (
    CustomerRefundRepository,
    CustomerReturnRepository,
)

__all__ = [
    "CustomerReturnRepository",
    "CustomerRefundRepository",
]
