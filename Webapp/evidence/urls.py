from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_evidence, name="upload_evidence"),
]

