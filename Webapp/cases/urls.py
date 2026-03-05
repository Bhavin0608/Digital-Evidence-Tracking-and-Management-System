from django.urls import path
from . import views

urlpatterns = [
    # Case detail (IMPORTANT — used in redirect)
    path("view/<int:case_id>/", views.case_detail, name="case_detail"),
    # Closure request
    path("request_closure/", views.request_closure, name="request_closure"),
    # Investigator: update case notes
    path("update_notes/", views.update_case_notes, name="update_case_notes"),
]