from django.contrib import admin
from django.contrib.auth.models import User
from .models import Case, CaseMember


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    list_display = (
        "case_id",
        "title",
        "priority",
        "status",
        "created_by",
        "assigned_so",
        "created_at",
    )

    list_filter = ("priority", "status")
    search_fields = ("case_id", "title")

    # 🔹 Filter dropdowns
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        # Only Admin in created_by dropdown
        if db_field.name == "created_by":
            kwargs["queryset"] = User.objects.filter(
                is_superuser = True
            )

        # Only Senior Officers in assigned_so dropdown
        if db_field.name == "assigned_so":
            kwargs["queryset"] = User.objects.filter(
                profile__role="SENIOR_OFFICER"
            )

        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )

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
