from django.urls import path
from . import views

urlpatterns = [

    # Case detail (IMPORTANT — used in redirect)
    path("<int:case_id>/", views.case_detail, name="case_detail"),

]