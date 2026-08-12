from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CashAndBankConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cash_and_bank"
    verbose_name = _("Enterprise Cash, Bank & Financial Reconciliation")
