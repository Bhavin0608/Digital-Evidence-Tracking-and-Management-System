from django.contrib import admin
from .models import Evidence, EvidenceNote


class EvidenceNoteInline(admin.TabularInline):
    model = EvidenceNote
    extra = 0
    readonly_fields = ("author", "content", "created_at")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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

    inlines = [EvidenceNoteInline]


@admin.register(EvidenceNote)
class EvidenceNoteAdmin(admin.ModelAdmin):
    list_display = ("evidence", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "author__username", "evidence__file_name")
    readonly_fields = ("evidence", "author", "content", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
