from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout

from users.models import UserProfile

def logout_view(request):
    logout(request)          # destroys session
    return redirect("login")  # redirect to login page

@never_cache
def root_redirect(request): # This is used to use root http://127.0.0.1:8000/ not explicit write home/ or login/ etc.

    if request.user.is_authenticated:

        user = request.user

        # 🔹 Check if profile exists
        if not hasattr(user, "profile"):
            return redirect("/admin/")

        role = user.profile.role

        if role == "SENIOR_OFFICER":
            return redirect("so_dashboard")

        elif role == "INVESTIGATOR":
            return redirect("investigator_dashboard")

        elif role == "AUDITOR":
            return redirect("auditor_dashboard")

        else:
            return redirect("login")

    else:
        return redirect("login")
@never_cache
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # 🔹 Check if profile exists # if admin trys to login in then it deny
            if not hasattr(user, "profile"):
                return render(
                    request,
                    "users/login.html",
                    {"error": "No authorized user exists."}
                )

            login(request, user)

            # 🔹 Get role
            role = user.profile.role

            # # 🔹 Redirect based on role
            if role == "SENIOR_OFFICER":
                return redirect("so_dashboard")

            elif role == "INVESTIGATOR":
                return redirect("investigator_dashboard")

            elif role == "AUDITOR":
                return redirect("auditor_dashboard")

        else:
            return render(
                request,
                "users/login.html",
                {"error": "Invalid credentials"}
            )

    return render(request, "users/login.html")

@never_cache
@login_required
def so_dashboard(request):
    return render(request, "users/so_dashboard.html")

@never_cache
@login_required
def investigator_dashboard(request):
    return render(request, "users/investigator_dashboard.html")

@never_cache
@login_required
def auditor_dashboard(request):
    return render(request, "users/auditor_dashboard.html")