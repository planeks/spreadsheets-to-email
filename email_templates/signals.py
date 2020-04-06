from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up
from email_templates.models import EmailSettings

User = get_user_model()


@receiver(user_signed_up, sender=User)
def create_email_settings(sender, request, user, **kwargs):
    """ Creates email settings for the user when he/she is regirested """
    email_settings = EmailSettings()
    test_email = user.email
    email_settings.test_email = test_email
    email_settings.user = user
    email_settings.save()
