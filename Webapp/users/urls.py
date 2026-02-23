from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    #---------------------------------- Dashboard URLs --------------------------------------
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/so/", views.so_dashboard, name="so_dashboard"),
    path("dashboard/investigator/", views.investigator_dashboard, name="investigator_dashboard"),
    path("dashboard/auditor/", views.auditor_dashboard, name="auditor_dashboard"),
    path("profile/", views.profile_view, name="profile"),
    #----------------------------------Cases URLs--------------------------------------------
    path("assign_investigators/", views.assign_investigators, name="assign_investigators"),
    path("monitor_progress/", views.monitor_progress, name="monitor_progress"),
    #---------------------------------- Logout URL ------------------------------------------
    path("logout/", views.logout_view, name="logout"),
]
