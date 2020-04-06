from django.test import TestCase
from .models import EmailTemplate
# Create your tests here.

class EmailTemplatesTestCase(TestCase):
    def setUp(self):
        template = EmailTemplate()