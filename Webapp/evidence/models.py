import hashlib
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

    file_name = models.CharField(
        max_length=255
    )

    file_type = models.CharField(
        max_length=100
    )

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

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        """
        Override save to generate SHA-256 hash
        only when evidence is first created.
        """
        if not self.sha256_hash:
            self.file_name = self.file.name
            self.file_type = self.file.name.split('.')[-1]
            self.file_size = self.file.size

            # Generate SHA-256
            sha256 = hashlib.sha256()
            for chunk in self.file.chunks():
                sha256.update(chunk)
            self.sha256_hash = sha256.hexdigest()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_name} ({self.case.case_id})"
