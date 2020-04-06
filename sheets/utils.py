"""Utils for different usage"""
import requests
import pytz
import json
from datetime import datetime, timedelta
from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponseRedirect
from google.oauth2.credentials import Credentials
from allauth.socialaccount.models import SocialAccount, SocialApp
from googleapiclient import discovery
from django.template import Template, Context


def custom_redirect(url_name, *args, **kwargs):
    """ Redirects to page with custom parameters
        Example: 
            Input: 
                url_name: 'email_templates:create_template'
                sheet_id: 3
            Output: http redirect to page: /templates/create/?sheet_id=3
    """
    url = reverse(url_name, args=args)
    params = urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


def generate_email_template(template, heads, data):
    """ Generates template from jinja template
        Example:
            Input: template (str): <h1>Hello, {{Student}}</h1> <p>Your marks: {{Mark1}}, {{Mark2}}</p>
                   heads (list): ['Student', 'Mark1', 'Mark2']
                   data (list): ['Maksym', 5, 4]
            Output: (str) <h1>Hello, Maksym</h1> <p>Your marks: 5, 4</p>

    """
    context = {}
    html_template = Template(template)
    for i, head in enumerate(heads):
        try:
            context[head] = data[i]
        except:
            context[head] = ""
    context = Context(context)
    html = html_template.render(context)
    return html


def get_google_sheets_service(request):
    """ Returns (obj) service for extracting user spreadsheets from google drive
    """
    google_app = SocialApp.objects.get(provider="google")
    user_account = SocialAccount.objects.get(user=request.user)
    user_token = user_account.socialtoken_set.first()
    client_id = google_app.client_id
    client_secret = google_app.secret
    refresh_token = user_token.token_secret
    utc = pytz.UTC

    expires_at = user_token.expires_at.replace(tzinfo=utc)
    now = utc.localize(datetime.now())

    if expires_at <= now:
        access_token = update_access_token(request)
    else:
        access_token = user_token.token
    # Credentials for sheets api
    credentials = Credentials(
        access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "profile",
            "email",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ],
    )
    # Service for working with sheets api
    service = discovery.build("sheets", "v4", credentials=credentials)
    return service


def update_access_token(request):
    """ Updates access token using refresh token
        Returns: (str) access token
    """
    google_app = SocialApp.objects.get(provider="google")
    user_account = SocialAccount.objects.get(user=request.user)
    user_token = user_account.socialtoken_set.first()
    client_id = google_app.client_id
    client_secret = google_app.secret
    refresh_token = user_token.token_secret
    request = requests.post(
        "https://www.googleapis.com/oauth2/v4/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    response = json.loads(request.content)
    user_token.token = response["access_token"]
    expires_in = response["expires_in"]
    expires_at = datetime.now() + timedelta(seconds=expires_in)
    user_token.expires_at = expires_at
    user_token.save()
    return user_token.token
