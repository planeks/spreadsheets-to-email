from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import SpreadSheet, EmailSeparator


class SpreadSheetForm(forms.ModelForm):
    class Meta:
        model = SpreadSheet
        fields = ("title", "spreadsheet_id", "user")


class SpreadSheetSettingsForm(forms.ModelForm):
    email_separator = forms.Field(
        label=_("Optional separator for multiple emails"),
        widget=forms.Select(
            attrs={"class": "form-control",},
            choices=[
                (tag.value, str(tag).split(".")[1] + f" [ {tag.value} ]")
                for tag in EmailSeparator
            ],
        ),
    )

    class Meta:
        model = SpreadSheet
        fields = ("id", "email", "bcc", "email_separator")
