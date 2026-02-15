from django.contrib import admin
from .models import Evidence


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "case",
        "file_name",
        "uploaded_by",
        "uploaded_at",
        "sha256_hash",
    )

    readonly_fields = ("sha256_hash", "uploaded_at")

    search_fields = ("file_name",)
    list_filter = ("case",)
