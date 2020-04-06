from enum import Enum
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from email_templates.models import EmailTemplate

User = get_user_model()


class EmailSeparator(Enum):
    Comma = ","
    Semicolon = ";"
    Colon = ":"


class SpreadSheet(models.Model):
    title = models.CharField(max_length=120, verbose_name=_("Title"))
    spreadsheet_id = models.TextField(verbose_name=_("Spreadsheet ID"))
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name="spreadsheets",
        verbose_name=_("Template"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="spreadsheets",
        verbose_name=_("User"),
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("Modified"))
    email_separator = models.CharField(max_length=1, verbose_name=_("Email Separator"))
    email = models.TextField(blank=True, null=True, verbose_name=_("CC"))
    bcc = models.TextField(blank=True, null=True, verbose_name=_("BCC"))

    class Meta:
        verbose_name_plural = _("spreadsheets")
        verbose_name = _("spreadsheet")

    def __str__(self):
        return self.title
