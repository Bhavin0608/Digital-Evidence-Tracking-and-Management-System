from django.db import models
from django.contrib.auth.models import User


class Case(models.Model):

    CATEGORY_CHOICES = [
        ("CYBER_CRIME", "Cyber Crime"),
        ("FRAUD", "Fraud"),
        ("THEFT", "Theft"),
        ("HOMICIDE", "Homicide"),
        ("NARCOTICS", "Narcotics"),
        ("ASSAULT", "Assault"),
        ("MISSING_PERSON", "Missing Person"),
        ("OTHER", "Other"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("PENDING_CLOSURE", "Pending Closure"),
        ("CLOSED", "Closed"),
    ]

    case_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for this case (e.g. CASE-2026-0001)"
    )

    title = models.CharField(
        max_length=200,
        help_text="Short descriptive title for the case"
    )

    description = models.TextField(
        help_text="Detailed description of the case"
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="Category of the case"
    )

    category_other = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Describe the category if 'Other' is selected"
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        help_text="Priority level of the case"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN",
        help_text="Current status of the case"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_cases",
        help_text="Admin who created this case"
    )

    assigned_so = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_cases",
        help_text="Senior Officer assigned to this case"
    )

    closure_summary = models.TextField(
        blank=True,
        null=True,
        help_text="Summary provided during closure request"
    )

    closure_requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closure_requests"
    )

    closure_requested_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Case"
        verbose_name_plural = "Cases"

    def __str__(self):
        return f"{self.case_id} — {self.title}"


class CaseMember(models.Model):

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="members",
        help_text="Case this investigator is assigned to"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="case_memberships",
        help_text="Investigator assigned to this case"
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("case", "user")
        ordering = ["-assigned_at"]
        verbose_name = "Case Member"
        verbose_name_plural = "Case Members"

    def __str__(self):
        return f"{self.user.username} → {self.case.case_id}"
