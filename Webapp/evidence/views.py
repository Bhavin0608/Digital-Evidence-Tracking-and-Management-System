from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from cases.models import Case
from .models import Evidence
from .forms import EvidenceUploadForm
from core.hash_service import HashService
from core.rbac_service import RBACService
from custody.models import CustodyLog
from django.contrib import messages

@login_required
def verify_evidence(request, evidence_id):
    evidence = get_object_or_404(Evidence, id=evidence_id)

    # RBAC check: user must be able to access the case
    if not RBACService.can_access_case(request.user, evidence.case):
        return HttpResponseForbidden("You do not have permission to verify this evidence.")

    # Recalculate hash
    is_valid = HashService.verify_hash(evidence.file, evidence.sha256_hash)

    # Log verification attempt
    CustodyLog.objects.create(
        case=evidence.case,
        evidence=evidence,
        performed_by=request.user,
        action_type="VERIFY",
        remarks="Integrity verified: VALID" if is_valid else "Integrity verified: COMPROMISED"
    )

    if is_valid:
        messages.success(request, "Evidence integrity verified successfully.")
    else:
        messages.error(request, "Evidence integrity compromised!")

    return redirect("case_detail", case_id=evidence.case_id)
from cases.models import Case, CaseMember

@login_required
def upload_evidence(request):

    # Fetch only cases assigned to this investigator
    assigned_cases = Case.objects.filter(
        members__user=request.user
    )

    if request.method == "POST":

        case_id = request.POST.get("case_id")
        case = get_object_or_404(Case, id=case_id)

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