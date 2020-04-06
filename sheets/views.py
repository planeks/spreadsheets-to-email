"""sheets views
"""
import json
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.template import Template, Context
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms.models import model_to_dict
from googleapiclient.errors import HttpError
from celery.result import AsyncResult
from email_templates.models import EmailTemplate
from .models import SpreadSheet
from .forms import SpreadSheetSettingsForm
from .utils import custom_redirect, get_google_sheets_service
from .tasks.send_emails import send_messages


def get_id_from_url(url):
    """ Returns a google spreadsheet id from the URL """
    try:
        spreadsheet_id = url.split("/")[5]
        return spreadsheet_id
    except IndexError:
        return None


def login(request):
    """ Displays login page """
    if request.user.is_authenticated:
        return redirect("sheets:sheet_list")
    return render(request, "login.html")


@login_required
def sheet_list(request):
    """ Displays user spreadsheets """
    sheets = request.user.spreadsheets
    if request.method == "POST":
        service = get_google_sheets_service(request)

        spreadsheet_id = get_id_from_url(request.POST.get("spreadsheet_id"))
        if not spreadsheet_id:
            messages.warning(request, _("Spreadsheet url is not correct"))
            return redirect("sheets:sheet_list")
        # Try to link a sheet
        try:
            title = (
                service.spreadsheets()
                .get(spreadsheetId=spreadsheet_id)
                .execute()["properties"]["title"]
            )

            sheet = SpreadSheet.objects.create(
                title=title, spreadsheet_id=spreadsheet_id, user=request.user
            )
        except HttpError:
            messages.warning(
                request,
                _(
                    "Spreadsheet url is not correct or you don't have \
                    a permission to see this spreadsheet"
                ),
            )
            return redirect("sheets:sheet_list")

        if sheet:
            messages.success(request, _("Spreadsheet is created"))
            return custom_redirect("sheets:choose_template", sheet_id=sheet.id)
    return render(request, "sheet_list.html", {"sheets": sheets})


@login_required
def delete_sheet(request, pk=None):
    """
    Deletes the spreadsheet by its id
    """
    sheet = get_object_or_404(SpreadSheet, pk=pk)
    sheet.delete()
    messages.success(request, _("Spreadsheet is detached"))
    return redirect("sheets:sheet_list")


@login_required
def sheet_preview(request, pk=None):
    """ Displays page with spreadsheet preview """
    sheet = get_object_or_404(SpreadSheet, pk=pk)
    if sheet.template:
        return render(request, "sheet_preview.html", {"spreadsheet": sheet})
    return custom_redirect("sheets:choose_template", sheet_id=sheet.id)


@login_required
def ajax_load_table(request, pk=None):
    """ Loads spreadsheet from Sheets api and displays table """
    service = get_google_sheets_service(request)
    # # The spreadsheet to request.
    sheet = get_object_or_404(SpreadSheet, pk=pk)
    spreadsheet_id = sheet.spreadsheet_id
    try:
        ranges = (
            service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id)
            .execute()["sheets"][0]["properties"]["title"]
        )
    except HttpError:
        return HttpResponse(_("The spreadsheet is not opened for you"))
    google_request = (
        service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=ranges)
    )
    response = google_request.execute()
    data = response["values"]
    heads = data[0]
    data = data[1:] if len(data) > 1 else []
    return render(
        request,
        "sheet_table.html",
        {
            "spreadsheet": sheet,
            "heads": heads,
            "data": data,
            "json_data": json.dumps(data),
            "json_heads": json.dumps(heads),
        },
    )


@login_required
def choose_template(request):
    """ Displays a form for choosing a template for the spreadsheet """
    sheet_id = request.GET.get("sheet_id")
    if not sheet_id:
        messages.warning(request, _("Oops, something wrong happened"))
        return redirect("sheets:sheet_list")
    templates = EmailTemplate.objects.filter(user=request.user)
    sheet = get_object_or_404(SpreadSheet, id=sheet_id)
    if request.method == "POST":
        template_id = request.POST.get("template")
        if template_id:
            template = get_object_or_404(EmailTemplate, id=template_id)
            sheet.template = template
            sheet.save()
            messages.success(
                request,
                mark_safe(
                    f'<b>{template.name}</b> {_("template is chosen")} for <b>{sheet.title}</b>'
                ),
            )
            return redirect("sheets:sheet_preview", pk=sheet.id)
    return render(
        request, "choose_template.html", {"sheet": sheet, "template_list": templates}
    )


@login_required
def ajax_load_preview(request, pk=None):
    """ Displays an HTML email template on spreadsheet preview page """
    if request.method != "POST":
        return HttpResponse("This method is not allowed")
    body = json.loads(request.body.decode("utf-8"))

    data = json.loads(body["data"])
    heads = json.loads(body["heads"])
    # # Get template for rendering
    template = get_object_or_404(SpreadSheet, pk=pk).template
    context = {}
    html_template = Template(template.html)
    for i, head in enumerate(heads):
        try:
            context[head] = data[i]
        except IndexError:
            context[head] = ""
    context = Context(context)
    html = html_template.render(context)
    return HttpResponse(html)


@login_required
def sheet_settings(request, pk=None):
    """ Displays the spreadsheet settings page """
    return render(request, "sheet_settings.html", {"spreadsheet_id": int(pk)})


@login_required
def ajax_load_sheet_settings(request, pk=None):
    """ Gets column data about the spreadsheet from sheets API and returns its settings """
    service = get_google_sheets_service(request)
    # The spreadsheet to request.
    sheet = get_object_or_404(SpreadSheet, pk=pk)
    spreadsheet_id = sheet.spreadsheet_id
    try:
        ranges = (
            service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id)
            .execute()["sheets"][0]["properties"]["title"]
        )
    except HttpError:
        return HttpResponse(_("The spreadsheet is not opened for you"))

    google_request = (
        service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=ranges)
    )
    response = google_request.execute()
    heads = response["values"][0]
    # Autoselect email
    if not sheet.email:
        if "Email" in heads:
            sheet.email = "Email"
            sheet.save()
        elif "email" in heads:
            sheet.email = "email"
            sheet.save()
    # Autoselect bcc
    if not sheet.bcc:
        if "Bcc" in heads:
            sheet.bcc = "Bcc"
            sheet.save()
        elif "bcc" in heads:
            sheet.bcc = "bcc"
            sheet.save()

    form = SpreadSheetSettingsForm(instance=sheet)
    if request.method == "POST":
        form = SpreadSheetSettingsForm(request.POST, instance=sheet)
        if form.is_valid():
            messages.success(request, _("Sheet is successfully edited"))
            form.save()
            return redirect("sheets:sheet_preview", pk=sheet.id)
    return render(
        request,
        "sheet_form.html",
        {
            "form": form,
            "heads": heads,
            "spreadsheet_email": sheet.email,
            "spreadsheet_bcc": sheet.bcc,
        },
    )


@login_required
def sheet_send_messages(request, pk=None):
    """
        Sends a email to recipients or to test email
        Input: pk (int) -> spreadsheet.id,
               data_index(int, optional) -> specific row from the data
    """
    sheet = get_object_or_404(SpreadSheet, id=pk)
    if not sheet.email:
        messages.warning(request, _("Please add information about your spreadsheet"))
        return redirect("sheets:sheet_settings", pk=sheet.id)
    data_index = request.GET.get("data_index")
    if data_index:
        data_index = int(data_index)

    template = sheet.template.html
    # Google API service
    service = get_google_sheets_service(request)
    spreadsheet_id = sheet.spreadsheet_id
    ranges = (
        service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id)
        .execute()["sheets"][0]["properties"]["title"]
    )
    # Get data from sheets api
    google_request = (
        service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=ranges)
    )
    response = google_request.execute()
    data = response["values"]
    email_settings = request.user.email_settings
    if (
        email_settings.smtp_host
        and email_settings.smtp_port
        and email_settings.smtp_username
        and email_settings.smtp_password
        and email_settings.smtp_from_email
    ):
        email_settings = model_to_dict(email_settings)
    else:
        email_settings = None
    # Send messages
    if data_index is not None:
        # Test message
        job = send_messages.s(
            data=data,
            sheet_title=sheet.title,
            template=template,
            data_index=data_index,
            email_to=request.user.email_settings.test_email,
            email_column=sheet.email,
            bcc_column=sheet.bcc,
            email_settings=email_settings,
        ).delay()
    else:
        # Real message
        job = send_messages.s(
            data=data,
            sheet_title=sheet.title,
            template=template,
            email_to=request.user.email_settings.test_email,
            email_column=sheet.email,
            bcc_column=sheet.bcc,
            email_settings=email_settings,
        ).delay()
    return render(request, "email_sending.html", {"job_id": job.id})


@login_required
def check_messages_status(request):
    """
        Checks statuses of sending messages (used for displaying progress bar)
    """
    if "job" in request.GET:
        job_id = request.GET["job"]
    else:
        return HttpResponse("Not valid url")
    job = AsyncResult(job_id)
    data = {"details": job.result, "state": job.state}
    return HttpResponse(json.dumps(data), content_type="application/json")
