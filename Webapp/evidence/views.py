from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from cases.models import Case, CaseMember
from .models import Evidence, EvidenceNote
from .forms import EvidenceUploadForm
from core.hash_service import HashService
from core.rbac_service import RBACService
from custody.models import CustodyLog
from django.contrib import messages
from django.http import FileResponse

@login_required
def preview_evidence(request, evidence_id):

    evidence = get_object_or_404(Evidence, id=evidence_id)

    if not RBACService.can_access_case(request.user, evidence.case):
        return HttpResponseForbidden("Access denied.")

    # Log PREVIEW (or use VIEW if you prefer)
    CustodyLog.objects.create(
        case=evidence.case,
        evidence=evidence,
        performed_by=request.user,
        action_type="VIEW",
        remarks="Evidence file previewed."
    )

    response = FileResponse(
        evidence.file.open("rb"),
        as_attachment=False,
        filename=evidence.file_name
    )

    # 🔥 Important: do NOT force download
    response["Content-Disposition"] = f'inline; filename="{evidence.file_name}"'

    return response
@login_required
def download_evidence(request, evidence_id):

    evidence = get_object_or_404(Evidence, id=evidence_id)

    if not RBACService.can_access_case(request.user, evidence.case):
        return HttpResponseForbidden("Access denied.")

    CustodyLog.objects.create(
        case=evidence.case,
        evidence=evidence,
        performed_by=request.user,
        action_type="DOWNLOAD",
        remarks="Evidence downloaded."
    )

    return FileResponse(
        evidence.file.open("rb"),
        as_attachment=True,
        filename=evidence.file_name
    )
@login_required
def evidence_detail(request, evidence_id):

    evidence = get_object_or_404(Evidence, id=evidence_id)

    # RBAC check
    if not RBACService.can_access_case(request.user, evidence.case):
        return HttpResponseForbidden("You do not have access to this evidence.")

    # 🔥 Create VIEW log
    CustodyLog.objects.create(
        case=evidence.case,
        evidence=evidence,
        performed_by=request.user,
        action_type="VIEW",
        remarks="Evidence viewed."
    )

    return render(request, "evidence/detail.html", {
        "evidence": evidence
    })
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

    return redirect("case_detail", case_id=evidence.case.id)
from cases.models import Case, CaseMember
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

        # if case.status != "IN_PROGRESS":
        #     return HttpResponseForbidden("Case is locked.")

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


# ======================== OBSERVATIONS PAGE ========================

@login_required
def observations(request):
    """Observations page — select case → see evidence → select evidence → view/add notes."""
    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins are not allowed to access this page.")

    if user.profile.role != "INVESTIGATOR":
        return HttpResponseForbidden("Access denied.")

    # Cases assigned to this investigator
    assigned_cases = Case.objects.filter(members__user=user)

    selected_case = None
    evidences = None
    selected_evidence = None
    notes = None

    # ---- Case selection via GET ----
    case_id = request.GET.get("case_id")
    if case_id:
        selected_case = get_object_or_404(Case, id=case_id)
        if not RBACService.can_access_case(user, selected_case):
            return HttpResponseForbidden("Access denied.")
        evidences = Evidence.objects.filter(case=selected_case).order_by("-uploaded_at")

    # ---- Evidence selection via GET ----
    evidence_id = request.GET.get("evidence_id")
    if evidence_id and selected_case:
        selected_evidence = get_object_or_404(Evidence, id=evidence_id, case=selected_case)
        notes = EvidenceNote.objects.filter(evidence=selected_evidence).select_related("author")

    # ---- Post a new note via POST ----
    if request.method == "POST" and selected_evidence:
        content = request.POST.get("content", "").strip()
        if content:
            EvidenceNote.objects.create(
                evidence=selected_evidence,
                author=user,
                content=content,
            )
            CustodyLog.objects.create(
                case=selected_evidence.case,
                evidence=selected_evidence,
                performed_by=user,
                action_type="VIEW",
                remarks=f"Observation added: {content[:80]}",
            )
            # Redirect to same page to avoid re-post on refresh
            return redirect(f"/evidence/observations/?case_id={selected_case.id}&evidence_id={selected_evidence.id}")

    return render(request, "evidence/observations.html", {
        "cases": assigned_cases,
        "selected_case": selected_case,
        "evidences": evidences,
        "selected_evidence": selected_evidence,
        "notes": notes,
    })