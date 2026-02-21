from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout

from cases.models import Case, CaseMember
from django.contrib.auth.models import User
from users.models import UserProfile

#------------------------------ Logout View ---------------------------------------
def logout_view(request):
    logout(request)          # destroys session
    return redirect("login")  # redirect to login page

#------------------------------ Root and Login Views -------------------------------
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

#------------------------------ Common dashboard redirection -------------------------------
@never_cache
@login_required
def dashboard_redirect(request): # for /dashboard/ url to redirect to respective dashboard based on role

    user = request.user

    if not hasattr(user, "profile"):
        return redirect("/admin/")

    role = user.profile.role

    if role == "SENIOR_OFFICER":
        return redirect("so_dashboard")

    elif role == "INVESTIGATOR":
        return redirect("investigator_dashboard")

    elif role == "AUDITOR":
        return redirect("auditor_dashboard")

    return redirect("login")

#------------------------------ Individual dashboards -------------------------------

@login_required
@never_cache
def so_dashboard(request):

    user = request.user

    # Superuser should use admin panel
    if user.is_superuser:
        return redirect("/admin/")

    # Ensure profile exists
    if not hasattr(user, "profile"):
        return HttpResponseForbidden("Unauthorized access.")

    # Role validation
    if user.profile.role != "SENIOR_OFFICER":
        return HttpResponseForbidden("Access denied.")

    return render(request, "users/so_dashboard.html")


@never_cache
@login_required
def investigator_dashboard(request):

    user = request.user

    if user.is_superuser:
        return redirect("/admin/")

    if not hasattr(user, "profile"):
        return HttpResponseForbidden("Unauthorized access.")

    if user.profile.role != "INVESTIGATOR":
        return HttpResponseForbidden("Access denied.")

    return render(request, "users/investigator_dashboard.html")


@never_cache
@login_required
def auditor_dashboard(request):

    user = request.user

    if user.is_superuser:
        return redirect("/admin/")

    if not hasattr(user, "profile"):
        return HttpResponseForbidden("Unauthorized access.")

    if user.profile.role != "AUDITOR":
        return HttpResponseForbidden("Access denied.")

    return render(request, "users/auditor_dashboard.html")


@never_cache
@login_required
def profile_view(request):
    return render(request, "users/profile.html")

#------------------------------ Cases related views -------------------------------
@never_cache
@login_required
def assign_investigators(request):
    user = request.user

    # Fetch only cases assigned to this SO
    cases = Case.objects.filter(
        assigned_so=user
    )

    investigators = User.objects.filter(
        profile__role="INVESTIGATOR"
    )

    if request.method == "POST": # after form submitted to assign investigators to the case
        print(request.POST)
        case_id = request.POST.get("case_id")

        investigator_ids = request.POST.getlist(
            "investigators"
        )

        case = Case.objects.get(id=case_id)

        for inv_id in investigator_ids:

            investigator = User.objects.get(id=inv_id)

            # Create membership (no role field now)
            CaseMember.objects.get_or_create(
                case=case,
                user=investigator
            )

        return redirect("so_dashboard")

    context = {
        "cases": cases,
        "investigators": investigators
    }
    return render(request, "users/assign_investigators.html", context)