from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SheetsConfig(AppConfig):
    name = "sheets"
    verbose_name = _("Spreadsheets")

