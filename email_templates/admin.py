from django.contrib import admin
from .models import EmailTemplate, EmailSettings


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'modified', 'created')
    search_fields = ('name', 'user')
    ordering = ('modified', 'created')

class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'test_email', 'smtp_host')
    search_fields = ('user',)


admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(EmailSettings, EmailSettingsAdmin)
