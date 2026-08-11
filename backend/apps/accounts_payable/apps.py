from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsPayableConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts_payable"
    verbose_name = _("Enterprise Supplier Invoices & Accounts Payable Foundation")
