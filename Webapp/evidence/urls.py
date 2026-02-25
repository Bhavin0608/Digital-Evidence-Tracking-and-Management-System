from django.urls import path
from . import views

urlpatterns = [
    path("preview/<int:evidence_id>/", views.preview_evidence, name="preview_evidence"),
    path("download/<int:evidence_id>/", views.download_evidence, name="download_evidence"),
    path("view/<int:evidence_id>/", views.evidence_detail, name="evidence_detail"),
    path("upload/", views.upload_evidence, name="upload_evidence"),
]

