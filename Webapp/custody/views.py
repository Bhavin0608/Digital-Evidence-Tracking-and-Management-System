from django.http import HttpResponseForbidden
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.hash_service import HashService
from evidence.models import Evidence
from .models import CustodyLog


@login_required
def custody_timeline(request):

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
    if request.user.profile.role != "AUDITOR":
        return HttpResponseForbidden("Not allowed")

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