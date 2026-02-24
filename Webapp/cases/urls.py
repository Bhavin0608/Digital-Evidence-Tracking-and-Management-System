from django.urls import path
from . import views

urlpatterns = [
    # Case detail (IMPORTANT — used in redirect)
    # Closure request
    path("request_closure/", views.request_closure, name="request_closure"),

]