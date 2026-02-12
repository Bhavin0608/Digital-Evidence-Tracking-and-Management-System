from django.contrib import admin
from .models import UserProfile


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
