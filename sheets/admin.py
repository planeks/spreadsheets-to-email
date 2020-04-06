from django.contrib import admin
from .models import SpreadSheet


class SpreadSheetAdmin(admin.ModelAdmin):
    list_display = ("title", "template", "user")
    search_fields = ("title",)


admin.site.register(SpreadSheet, SpreadSheetAdmin)
