from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsReceivableConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts_receivable"
    verbose_name = _("Enterprise Customer Accounts Receivable (AR)")
