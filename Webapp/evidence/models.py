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
