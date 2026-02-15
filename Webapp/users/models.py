from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("SENIOR_OFFICER", "Senior Officer"),
        ("INVESTIGATOR", "Investigator"),
        ("AUDITOR", "Auditor"),
    ]

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    dob = models.DateField(
        null=True,
        blank=False
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=False
    )

    badge_number = models.CharField(
        max_length=50,
        null=True,
        blank=False
    )

    department = models.CharField(
        max_length=100,
        null=True,
        blank=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ===== Helper Methods =====

    def is_senior_officer(self):
        return self.role == "SENIOR_OFFICER"

    def is_investigator(self):
        return self.role == "INVESTIGATOR"

    def is_auditor(self):
        return self.role == "AUDITOR"

    def __str__(self):
        return f"{self.user.username} - {self.role}"
