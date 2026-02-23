from django.urls import path
from . import views
from .views import verify_evidence

urlpatterns = [
    path("verify/<int:evidence_id>/", verify_evidence, name="verify_evidence"),
    path("upload/", views.upload_evidence, name="upload_evidence"),
]

