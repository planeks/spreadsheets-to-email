"""config URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from email_templates.views import email_settings, test_smtp_connection
from sheets.views import login

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sheets/", include("sheets.urls")),
    path("accounts/", include("allauth.urls")),
    path("templates/", include("email_templates.urls")),
    path("email/settings/", email_settings, name="email_settings"),
    path("email/test/", test_smtp_connection, name="test_smtp_connection"),
    path("", login, name="login"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
