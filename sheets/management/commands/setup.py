import os
from decouple import config
from allauth.socialaccount.models import SocialApp
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

# Import .env vars
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", None)
DOMAIN = config("DOMAIN", None)


class Command(BaseCommand):
    def handle(self, *args, **options):

        # Run migrations
        call_command("migrate", interactive=False)

        if DOMAIN == "None":
            self.stdout.write(self.style.ERROR("Please add DOMAIN to your .env file"))
            return None
        if GOOGLE_CLIENT_SECRET == "None":
            self.stdout.write(
                self.style.ERROR("Please add GOOGLE_CLIENT_SECRET to your .env file")
            )
            return None
        if GOOGLE_CLIENT_ID == "None":
            self.stdout.write(
                self.style.ERROR("Please add GOOGLE_CLIENT_ID to your .env file")
            )
            return None

        # Edit site
        current_site = Site.objects.get_current()
        current_site.name = DOMAIN
        current_site.domain = DOMAIN
        current_site.save()

        # Add google app to Social Applications
        google_app = SocialApp.objects.filter(provider="google")
        if not google_app.exists():
            google_app = SocialApp.objects.create(
                provider="google",
                name="Google",
                client_id=GOOGLE_CLIENT_ID,
                secret=GOOGLE_CLIENT_SECRET,
            )
            google_app.sites.add(current_site)
            google_app.save()

        self.stdout.write(self.style.SUCCESS("Successfully build!"))
