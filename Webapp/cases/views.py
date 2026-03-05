from unittest import case
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Case, CaseMember
from django.utils import timezone
from django.http import HttpResponseForbidden
from custody.models import CustodyLog
from core.rbac_service import RBACService
@login_required
def case_detail(request, case_id):

    case = get_object_or_404(Case, id=case_id)

    # RBAC check
    if not RBACService.can_access_case(request.user, case):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have access to this case.")

    return render(request, "cases/case_detail.html", {
        "case": case
    })
@login_required
def request_closure(request):
    # Only cases assigned to SO and not already closed
    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins Are not allowed to access this page.")
    
    if user.profile.role != "SENIOR_OFFICER":
        return HttpResponseForbidden("Access denied.")
    
    cases = Case.objects.filter(
        assigned_so=request.user,
        status="OPEN"
    )
    
    if request.method == "POST":

        case_id = request.POST.get("case_id")
        summary = request.POST.get("summary")

        case = get_object_or_404(Case, id=case_id)

        # Security check
        if case.assigned_so != request.user:
            return HttpResponseForbidden("Not allowed")
        
        if case.status != "OPEN":
            return HttpResponseForbidden("Case not eligible for closure")

        case.status = "PENDING_CLOSURE"
        case.closure_summary = summary
        case.closure_requested_by = request.user
        case.closure_requested_at = timezone.now()
        case.save()

        # Log it
        CustodyLog.objects.create(
            case=case,
            performed_by=request.user,
            action_type="CLOSURE_REQUEST",
            remarks="Closure requested by Senior Officer"
        )

        return redirect("so_dashboard")

    return render(request, "cases/request_closure.html", {
        "cases": cases
    })


@login_required
def update_case_notes(request):
    """Investigator selects an assigned case, updates title/description/priority."""
    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins are not allowed to access this page.")

    if user.profile.role != "INVESTIGATOR":
        return HttpResponseForbidden("Access denied.")

    # Cases assigned to this investigator
    assigned_cases = Case.objects.filter(members__user=user)

    selected_case = None
    success = False

    # ---- Case selection via GET ----
    case_id = request.GET.get("case_id")
    if case_id:
        selected_case = get_object_or_404(Case, id=case_id)
        # Verify assignment
        if not CaseMember.objects.filter(case=selected_case, user=user).exists():
            return HttpResponseForbidden("You are not assigned to this case.")

    # ---- Update via POST ----
    if request.method == "POST":
        case_id = request.POST.get("case_id")
        selected_case = get_object_or_404(Case, id=case_id)

        if not CaseMember.objects.filter(case=selected_case, user=user).exists():
            return HttpResponseForbidden("You are not assigned to this case.")

        # Only update allowed fields
        new_title = request.POST.get("title", "").strip()
        new_description = request.POST.get("description", "").strip()
        new_priority = request.POST.get("priority", "").strip()

        changes = []

        if new_title and new_title != selected_case.title:
            selected_case.title = new_title
            changes.append("title")

        if new_description and new_description != selected_case.description:
            selected_case.description = new_description
            changes.append("description")

        if new_priority in dict(Case.PRIORITY_CHOICES) and new_priority != selected_case.priority:
            selected_case.priority = new_priority
            changes.append("priority")

        if changes:
            selected_case.save()
            CustodyLog.objects.create(
                case=selected_case,
                performed_by=user,
                action_type="CASE_UPDATE",
                remarks=f"Case updated by investigator. Fields changed: {', '.join(changes)}",
            )
            success = True

        # Redirect to avoid re-post
        if success:
            return redirect(f"/cases/update_notes/?case_id={selected_case.id}&updated=1")

    updated = request.GET.get("updated") == "1"

    return render(request, "cases/update_case_notes.html", {
        "cases": assigned_cases,
        "selected_case": selected_case,
        "updated": updated,
    })