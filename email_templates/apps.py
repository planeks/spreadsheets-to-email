from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EmailTemplatesConfig(AppConfig):
    name = "email_templates"
    verbose_name = _("Email Templates")

    def ready(self):
        import email_templates.signals
