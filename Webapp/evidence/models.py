from django.db import models
from django.contrib.auth.models import User
from cases.models import Case


class Evidence(models.Model):

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="evidences"
    )

    file = models.FileField(
        upload_to="evidence_files/"
    )

    file_name = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
        default="",
        help_text="Brief description of the evidence"
    )

    file_type = models.CharField(max_length=100)

    file_size = models.BigIntegerField()

    sha256_hash = models.CharField(
        max_length=64,
        editable=False
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_evidences"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} ({self.case.case_id})"


class EvidenceNote(models.Model):
    """Observation / comment attached to a specific evidence item."""

    evidence = models.ForeignKey(
        Evidence,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evidence_notes"
    )

    content = models.TextField(
        help_text="Observation or comment text"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Evidence Note"
        verbose_name_plural = "Evidence Notes"

    def __str__(self):
        return f"Note by {self.author.username} on {self.evidence.file_name}"
