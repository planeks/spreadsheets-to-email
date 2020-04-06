from django.urls import path, include
from .views import (
    sheet_list,
    delete_sheet,
    sheet_preview,
    ajax_load_table,
    choose_template,
    ajax_load_preview,
    sheet_settings,
    ajax_load_sheet_settings,
    sheet_send_messages,
    check_messages_status,
)

app_name = "sheets"

urlpatterns = [
    path("", sheet_list, name="sheet_list"),
    path("<int:pk>/delete/", delete_sheet, name="sheet_delete"),
    path("<int:pk>/", sheet_preview, name="sheet_preview"),
    path("<int:pk>/table/", ajax_load_table, name="ajax_load_table"),
    path("template/", choose_template, name="choose_template"),
    path("<int:pk>/preview/", ajax_load_preview, name="ajax_load_preview"),
    path("<int:pk>/settings/", sheet_settings, name="sheet_settings"),
    path(
        "<int:pk>/settings/load/",
        ajax_load_sheet_settings,
        name="ajax_load_sheet_settings",
    ),
    path("<int:pk>/messages/send/", sheet_send_messages, name="sheet_send_messages",),
    path("messages/status/", check_messages_status, name="check_messages_status"),
]
