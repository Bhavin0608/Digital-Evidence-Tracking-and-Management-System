from django.utils import timezone
import uuid

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cases.models import Case
from core.hash_service import HashService
from evidence.models import Evidence
from .models import CustodyLog


@login_required
def custody_timeline(request):

    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins Are not allowed to access this page.")

    if request.user.profile.role != "AUDITOR":
        return HttpResponseForbidden("Not allowed")

    evidences = Evidence.objects.all()

    selected_evidence = None
    logs = None

    evidence_id = request.GET.get("evidence_id")

    if evidence_id:
        selected_evidence = Evidence.objects.get(id=evidence_id)

        logs = CustodyLog.objects.filter(
            evidence=selected_evidence
        ).order_by("timestamp")

    return render(
        request,
        "custody/timeline.html",
        {
            "evidences": evidences,
            "selected_evidence": selected_evidence,
            "logs": logs
        }
    )

@login_required
def integrity_console(request):

    # Only Auditor allowed
    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins Are not allowed to access this page.")
    
    if user.profile.role != "AUDITOR":
        return HttpResponseForbidden("Access denied.")

    evidences = Evidence.objects.select_related("case").all()

    results = []

    if request.method == "POST":
        for evidence in evidences:

            is_valid = HashService.verify_hash(
                evidence.file,
                evidence.sha256_hash
            )

            # Log each verification
            CustodyLog.objects.create(
                case=evidence.case,
                evidence=evidence,
                performed_by=request.user,
                action_type="VERIFY",
                remarks="Integrity verified: VALID"
                        if is_valid
                        else "Integrity verified: COMPROMISED"
            )

            results.append({
                "evidence": evidence,
                "original_hash": evidence.sha256_hash,
                "current_hash": HashService.generate_sha256(evidence.file),
                "is_valid": is_valid
            })

    return render(
        request,
        "custody/integrity_console.html",
        {
            "results": results,
            "evidences": evidences
        }
    )

@login_required
def generate_report(request):

    # Only Auditor
    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins Are not allowed to access this page.")
    
    if user.profile.role != "AUDITOR":
        return HttpResponseForbidden("Access denied.")

    cases = Case.objects.all().order_by("-created_at")

    selected_case = None
    evidences = None
    reference_id = None

    case_id = request.GET.get("case_id")

    if case_id:
        selected_case = get_object_or_404(Case, id=case_id)
        evidences = Evidence.objects.filter(case=selected_case)

        reference_id = f"AUD-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"

    return render(
        request,
        "custody/generate_report.html",
        {
            "cases": cases,
            "selected_case": selected_case,
            "evidences": evidences,
            "reference_id": reference_id,
            "today": timezone.now()
        }
    )