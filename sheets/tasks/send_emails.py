from time import sleep
from celery import current_task
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from config.celery import app
from sheets.utils import generate_email_template, get_google_sheets_service


@app.task
def send_messages(data, template, sheet_title, data_index=None, email_to=None, email_column=None, bcc_column=None, email_splitter=',', email_settings=None):
    heads = data[0]

    if email_settings:
        smtp_host = email_settings['smtp_host']
        smtp_port = email_settings['smtp_port']
        smtp_username = email_settings['smtp_username']
        smtp_password = email_settings['smtp_password']

        mail_backend = EmailBackend(
            host=smtp_host,
            port=smtp_port,
            password=smtp_password,
            username=smtp_username,
            use_tls=True,
            timeout=10
        )
    else:
        mail_backend = None
    if data_index != None:
        data = data[1:][data_index]
        current_task.update_state(state='PROGRESS',
                                  meta={'current': 0, 'total': 1})
        html_template = generate_email_template(template, heads, data)
        if email_settings:
            pass
            from_email = email_settings['smtp_from_email']
        else:
            from_email = settings.DEFAULT_FROM_EMAIL
        if email_to:
            sended = send_mail(
                sheet_title, message=strip_tags(html_template), html_message=html_template, recipient_list=(email_to,),
                from_email=from_email, connection=mail_backend
            )
            current_task.update_state(state='PROGRESS',
                                      meta={'current': 1, 'total': 1})
    else:
        data = data[1:]
        data_size = len(data)
        current_task.update_state(state='PROGRESS',
                                  meta={'current': 0, 'total': data_size})

        if email_column:
            email_column_index = heads.index(email_column)
        else:
            email_column_index = None

        if bcc_column:
            bcc_column_index = heads.index(bcc_column)
        else:
            bcc_column_index = None

        for i, el_data in enumerate(data):
            sleep(1)
            email_to = el_data[email_column_index]
            html_template = generate_email_template(template, heads, el_data)
            if email_settings:
                from_email = email_settings['smtp_from_email']
            else:
                from_email = settings.DEFAULT_FROM_EMAIL
            msg = EmailMultiAlternatives(subject=sheet_title, body=strip_tags(
                html_template), from_email=from_email)
            msg.attach_alternative(html_template, 'text/html')
            if bcc_column_index:
                msg.bcc = el_data[bcc_column_index].split(email_splitter)
            if email_column_index:
                msg.cc = el_data[email_column_index].split(email_splitter)
            if mail_backend:
                msg.connection = mail_backend

            msg.send()

            current_task.update_state(state='PROGRESS',
                                      meta={'current': i, 'total': data_size})
