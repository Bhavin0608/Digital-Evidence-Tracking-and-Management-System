from django.contrib import admin
from .models import CustodyLog


@admin.register(CustodyLog)
class CustodyLogAdmin(admin.ModelAdmin):
    list_display = ("case", "action_type", "performed_by", "timestamp")
    readonly_fields = [field.name for field in CustodyLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False