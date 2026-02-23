from django.urls import path
from . import views


urlpatterns = [
    path("timeline/", views.custody_timeline, name="timeline"),
]