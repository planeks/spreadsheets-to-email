from django import forms
from .models import EmailSettings


class EmailSettingsForm(forms.ModelForm):
    test_email = forms.Field(
        required=True, widget=forms.TextInput(attrs={"class": "form-control",})
    )
    smtp_from_email = forms.Field(
        required=False, widget=forms.TextInput(attrs={"class": "form-control",})
    )
    smtp_host = forms.Field(
        required=False, widget=forms.TextInput(attrs={"class": "form-control",})
    )
    smtp_port = forms.Field(
        required=False, widget=forms.NumberInput(attrs={"class": "form-control","value": 587})
    )
    smtp_username = forms.Field(
        required=False, widget=forms.TextInput(attrs={"class": "form-control",})
    )
    smtp_password = forms.Field(
        required=False,
        widget=forms.PasswordInput(render_value=True, attrs={"class": "form-control",}),
    )

    class Meta:
        model = EmailSettings
        fields = (
            "test_email",
            "smtp_host",
            "smtp_port",
            "smtp_username",
            "smtp_password",
            "smtp_from_email",
        )
