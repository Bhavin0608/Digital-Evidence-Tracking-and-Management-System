from django import forms
from .models import Evidence


class EvidenceUploadForm(forms.ModelForm):

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB limit

    class Meta:
        model = Evidence
        fields = ["file"]

    def clean_file(self):
        file = self.cleaned_data.get("file")

        if not file:
            raise forms.ValidationError("No file uploaded.")

        # 🔹 Validate file size
        if file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError("File size exceeds 100 MB limit.")

        # 🔹 Validate file type (basic check)
        allowed_extensions = [
            ".pdf", ".jpg", ".jpeg", ".png",
            ".doc", ".docx", ".txt", ".zip"
        ]

        file_name = file.name.lower()

        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError("Unsupported file type.")

        return file
