from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from .models import Case, CaseMember


# ── Inline: assign investigators from the Case page ──────────────

class CaseMemberInline(admin.TabularInline):
    model = CaseMember
    extra = 1
    readonly_fields = ("assigned_at",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(
                profile__role="INVESTIGATOR"
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ── Case admin form with category_other validation ───────────────

class CaseAdminForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        category_other = cleaned_data.get("category_other", "").strip()

        if category == "OTHER" and not category_other:
            raise ValidationError(
                {"category_other": "Please describe the category when 'Other' is selected."}
            )

        if category != "OTHER" and category_other:
            cleaned_data["category_other"] = ""

        return cleaned_data


# ── Case admin ────────────────────────────────────────────────────

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    form = CaseAdminForm

    list_display = (
        "case_id",
        "title",
        "category",
        "priority",
        "status",
        "created_by",
        "assigned_so",
        "created_at",
    )

    list_filter = ("priority", "status", "category")
    search_fields = ("case_id", "title")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    inlines = [CaseMemberInline]

    fieldsets = (
        ("Case Information", {
            "fields": (
                "case_id",
                "title",
                "description",
                "category",
                "category_other",
            ),
        }),
        ("Priority & Status", {
            "fields": ("priority", "status"),
        }),
        ("Assignment", {
            "fields": ("created_by", "assigned_so"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # 🔹 Filter dropdowns
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        # Only Admin in created_by dropdown
        if db_field.name == "created_by":
            kwargs["queryset"] = User.objects.filter(
                is_superuser=True
            )

        # Only Senior Officers in assigned_so dropdown
        if db_field.name == "assigned_so":
            kwargs["queryset"] = User.objects.filter(
                profile__role="SENIOR_OFFICER"
            )

        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )


# ── CaseMember admin ─────────────────────────────────────────────

@admin.register(CaseMember)
class CaseMemberAdmin(admin.ModelAdmin):

    list_display = (
        "case",
        "user",
        "assigned_at",
    )

    list_filter = (
        "assigned_at",
    )

    search_fields = (
        "case__case_id",
        "user__username",
    )

    ordering = ("-assigned_at",)

    # 🔹 Filter dropdown to show only Investigators
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(
                profile__role="INVESTIGATOR"
            )

        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )
