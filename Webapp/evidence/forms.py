from django import forms
from .models import Evidence


class EvidenceUploadForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ["file"]
