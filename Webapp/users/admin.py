from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


# ── UserProfile inline on User ─────────────────────────────────
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Officer Profile"
    verbose_name_plural = "Officer Profile"
    fieldsets = (
        (None, {
            "fields": ("role", "badge_number", "department", "dob", "gender"),
        }),
    )


# ── Custom User Admin ──────────────────────────────────────────
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = (
        "username", "first_name", "last_name", "email",
        "get_role", "get_badge", "get_department", "is_active",
    )
    list_filter = ("is_active", "profile__role", "profile__department")
    search_fields = ("username", "first_name", "last_name", "email", "profile__badge_number")

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except UserProfile.DoesNotExist:
            return "—"
    get_role.short_description = "Role"
    get_role.admin_order_field = "profile__role"

    def get_badge(self, obj):
        try:
            return obj.profile.badge_number or "—"
        except UserProfile.DoesNotExist:
            return "—"
    get_badge.short_description = "Badge #"

    def get_department(self, obj):
        try:
            return obj.profile.department or "—"
        except UserProfile.DoesNotExist:
            return "—"
    get_department.short_description = "Department"


# Unregister default User admin --> re-register with our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ── Standalone UserProfile admin ───────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "badge_number",
        "department",
        "created_at",
    )

    list_filter = ("role", "department")
    search_fields = ("user__username", "badge_number")
