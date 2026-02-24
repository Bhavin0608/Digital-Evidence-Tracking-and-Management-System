from django.urls import path
from . import views


urlpatterns = [
    path("timeline/", views.custody_timeline, name="timeline"),
    path("integrity/", views.integrity_console, name="integrity_console"),
    path("report/", views.generate_report, name="generate_report"),
]