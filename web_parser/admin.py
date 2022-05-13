from django.contrib import admin

from web_parser.models import RegistrationCredential


@admin.register(RegistrationCredential)
class RegistrationDataAdmin(admin.ModelAdmin):
    pass
