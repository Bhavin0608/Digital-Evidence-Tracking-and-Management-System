from unittest import case
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from cases.models import Case, CaseMember
from .models import Evidence
from .forms import EvidenceUploadForm
from core.hash_service import HashService
from core.rbac_service import RBACService
from custody.models import CustodyLog
from django.contrib import messages

@login_required
def upload_evidence(request):
    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins Are not allowed to access this page.")
    
    if user.profile.role != "INVESTIGATOR":
        return HttpResponseForbidden("Access denied.")

    # Fetch only cases assigned to this investigator
    assigned_cases = Case.objects.filter(
        members__user=request.user
    )

    if request.method == "POST":

        case_id = request.POST.get("case_id")
        case = get_object_or_404(Case, id=case_id)

        if case.status != "IN_PROGRESS":
            return HttpResponseForbidden("Case is locked.")

        # RBAC check
        if not CaseMember.objects.filter(
            case=case,
            user=request.user
        ).exists():
            return HttpResponseForbidden("Not assigned to this case.")

        file = request.FILES.get("file")

        if file:
            sha256_hash = HashService.generate_sha256(file)

            evidence = Evidence.objects.create(
                case=case,
                file=file,
                file_name=file.name,
                file_type=file.content_type,
                file_size=file.size,
                sha256_hash=sha256_hash,
                uploaded_by=request.user
            )

            CustodyLog.objects.create(
                case=case,
                evidence=evidence,
                performed_by=request.user,
                action_type="UPLOAD",
                remarks="Evidence uploaded."
            )

            return redirect("investigator_dashboard")

    return render(request, "evidence/upload.html", {
        "cases": assigned_cases
    })