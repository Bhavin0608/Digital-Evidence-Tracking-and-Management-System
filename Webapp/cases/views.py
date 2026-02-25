from unittest import case
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Case
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