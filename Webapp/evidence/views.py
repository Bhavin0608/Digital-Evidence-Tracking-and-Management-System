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
@login_required
def upload_evidence(request, case_id):

    case = get_object_or_404(Case, pk=case_id)


    # ===== RBAC CHECK (Temporary Basic Check) =====
    if not RBACService.can_upload_evidence(request.user, case):
        return HttpResponseForbidden("You do not have permission to upload evidence.")

    if request.method == "POST":
        form = EvidenceUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data["file"]


            sha256_hash = HashService.generate_sha256(file)

            evidence = Evidence.objects.create(
                case=case,
                file=file,
                file_name=file.name,
                file_type = file.content_type,
                file_size=file.size,
                sha256_hash=sha256_hash,
                uploaded_by=request.user
            )

            # CustodyLog will be added later

            CustodyLog.objects.create(
                case=case,
                evidence=evidence,
                performed_by=request.user,
                action_type="UPLOAD",
                remarks="Evidence uploaded to case."
            )
            return redirect("case_detail", case_id=case.id)

    else:
        form = EvidenceUploadForm()

    return render(request, "evidence/upload.html", {
        "form": form,
        "case": case
    })
