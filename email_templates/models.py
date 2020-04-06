from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


User = get_user_model()


class EmailTemplate(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("User"), related_name="templates"
    )
    name = models.CharField(max_length=120, verbose_name=_("Template"))
    html = models.TextField(verbose_name=_("HTML"))
    content = models.TextField(verbose_name=_("Content"))
    modified = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name=_("Modified")
    )
    created = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name=_("Created")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("email template")
        verbose_name_plural = _("email templates")


class EmailSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="email_settings",
    )
    test_email = models.CharField(
        max_length=120, null=True, blank=True, verbose_name=_("Test Email")
    )
    smtp_host = models.CharField(
        max_length=120, null=True, blank=True, verbose_name=_("SMTP Host")
    )
    smtp_port = models.IntegerField(null=True, blank=True, verbose_name=_("SMTP Port"))
    smtp_username = models.CharField(
        max_length=120, null=True, blank=True, verbose_name=_("SMTP Username")
    )
    smtp_password = models.CharField(
        max_length=120, null=True, blank=True, verbose_name=_("SMTP Password")
    )
    smtp_from_email = models.CharField(
        max_length=120, null=True, blank=True, verbose_name=_("From email")
    )

    def __str__(self):
        return f"{self.user.email} | {self.test_email}"

    class Meta:
        verbose_name_plural = _("email settings")
        verbose_name = _("email settings")
