from django.db import models
from django.contrib.auth.models import User
from cases.models import Case
from evidence.models import Evidence


class CustodyLog(models.Model):

    ACTION_CHOICES = [
        ("UPLOAD", "Evidence Uploaded"),
        ("VIEW", "Evidence Viewed"),
        ("VERIFY", "Evidence Verified"),
        ("DOWNLOAD", "Evidence Downloaded"),
        ("INVESTIGATOR_ASSIGNED", "Investigator Assigned"),
        ("CASE_UPDATE", "Case Updated"),
        ("CLOSURE_REQUEST", "Case Closure Requested"),
        ("CASE_CLOSED", "Case Closed"),
    ]

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="custody_logs"
    )

    evidence = models.ForeignKey(
        Evidence,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="custody_logs"
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    action_type = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
    

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("CustodyLog entries cannot be updated.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action_type} - {self.case.case_id} - {self.timestamp}"