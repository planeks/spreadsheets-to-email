""" email_templates views """
from smtplib import SMTPException
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
from sheets.models import SpreadSheet
from .models import EmailTemplate
from .forms import EmailSettingsForm


@login_required
def create_template(request):
    """Displays form for creating an email template"""
    sheet_id = request.GET.get("sheet_id")
    if request.method == "POST":
        name = request.POST.get("title")
        content = request.POST.get("content")
        html = request.POST.get("template-html")
        email_template = EmailTemplate()
        email_template.name = name
        email_template.html = html
        email_template.user = request.user
        email_template.content = content
        email_template.save()
        messages.success(request, _("Template was created"))
        if sheet_id:
            sheet = get_object_or_404(SpreadSheet, id=sheet_id)
            sheet.template = email_template
            sheet.save()
            return redirect("sheets:sheet_preview", pk=sheet.id)
        return redirect("email_templates:template_list")

    return render(
        request,
        "template_form.html",
        {
            "create_template": True,
            "beeplugin_client_id": settings.BEEPLUGIN_CLIENT_ID,
            "beeplugin_client_secret": settings.BEEPLUGIN_CLIENT_SECRET,
        },
    )


@login_required
def template_list(request):
    """Displays all email templates of the user"""
    templates = EmailTemplate.objects.filter(user=request.user)
    return render(request, "template_list.html", {"template_list": templates})


@login_required
def edit_template(request, pk=None):
    """Displays form for editing an email template"""
    email_template = get_object_or_404(EmailTemplate, id=pk)
    if request.method == "POST":
        name = request.POST.get("title")
        content = request.POST.get("content")
        html = request.POST.get("template-html")
        if name and content and html:
            email_template.name = name
            email_template.html = html
            email_template.content = content
            email_template.save()
        messages.success(request, _("Template was edited"))

        return redirect("email_templates:template_list")

    return render(
        request,
        "template_form.html",
        {
            "template": email_template,
            "beeplugin_client_id": settings.BEEPLUGIN_CLIENT_ID,
            "beeplugin_client_secret": settings.BEEPLUGIN_CLIENT_SECRET,
        },
    )


@login_required
def delete_template(request, pk=None):
    """Deletes the email template"""
    template = get_object_or_404(EmailTemplate, id=pk)
    template.delete()
    messages.success(request, _("Template is deleted"))
    return redirect("email_templates:template_list")


@login_required
def email_settings(request):
    """Displays form for editing an SMTP settings"""
    user = request.user
    form = EmailSettingsForm(instance=user.email_settings)

    if request.method == "POST":
        form = EmailSettingsForm(request.POST, instance=user.email_settings)
        if form.is_valid():
            form.save()
            messages.success(request, _("Email settings are updated"))
            return redirect("email_settings")
        messages.success(request, _("Oops, try again"))
        return redirect("email_settings")
    return render(request, "email_settings.html", {"form": form})


@login_required
def test_smtp_connection(request):
    """ Tests smtp connection """
    mail_backend = EmailBackend(
        host=request.user.email_settings.smtp_host,
        port=request.user.email_settings.smtp_port,
        password=request.user.email_settings.smtp_password,
        username=request.user.email_settings.smtp_username,
        use_tls=True,
        timeout=10,
    )
    try:
        mail_backend.open()
        mail_backend.close()
        messages.success(
            request,
            _("SMTP settings are correct. Now you are using it for email sending"),
        )
    except SMTPException:
        messages.warning(
            request,
            _(
                "SMTP settings are not correct. Please provide correct credentials \
                and make sure that your smtp is running"
            ),
        )
    return redirect("email_settings")
