from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from users.models import UserProfile

def root_redirect(request): # This is used to use root http://127.0.0.1:8000/ not explicit write home/ or login/ etc.

    if request.user.is_authenticated:
        return redirect("home")   # logged-in landing page
    else:
        return redirect("login")  # login page

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

            login(request, user)

            # 🔹 Get role
            # role = user.profile.role

            # # 🔹 Redirect based on role
            # if role == "SENIOR_OFFICER":
            #     return redirect("so_dashboard")

            # elif role == "INVESTIGATOR":
            #     return redirect("investigator_dashboard")

            # elif role == "AUDITOR":
            #     return redirect("auditor_dashboard")
            return redirect("home")


        else:
            return render(
                request,
                "users/login.html",
                {"error": "Invalid credentials"}
            )

    return render(request, "users/login.html")

@login_required
def home(request):
    return render(request, "users/home.html")
