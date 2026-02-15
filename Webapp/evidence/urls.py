from django.urls import path
from . import views

urlpatterns = [
    path("upload/<int:case_id>/", views.upload_evidence, name="upload_evidence"),
]
