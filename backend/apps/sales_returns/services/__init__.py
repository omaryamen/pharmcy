"""Export services for apps.sales_returns."""

from apps.sales_returns.services.number_generator import SalesReturnNumberGenerator
from apps.sales_returns.services.returns_service import CustomerReturnService

__all__ = [
    "SalesReturnNumberGenerator",
    "CustomerReturnService",
]
