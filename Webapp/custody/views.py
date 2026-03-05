from django.utils import timezone
from django.db.models import Count
import uuid

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from cases.models import Case, CaseMember
from core.hash_service import HashService
from evidence.models import Evidence, EvidenceNote
from .models import CustodyLog


@login_required
def custody_timeline(request):

    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins are not allowed to access this page.")

    if user.profile.role != "AUDITOR":
        return HttpResponseForbidden("Not allowed")

    # All cases and evidences for filtering
    cases = Case.objects.all().order_by("-created_at")
    evidences = Evidence.objects.select_related("case").all()

    selected_case = None
    selected_evidence = None
    logs = None

    case_id = request.GET.get("case_id")
    evidence_id = request.GET.get("evidence_id")

    # Filter evidences by case if selected
    if case_id:
        selected_case = get_object_or_404(Case, id=case_id)
        evidences = evidences.filter(case=selected_case)

    if evidence_id:
        selected_evidence = get_object_or_404(Evidence, id=evidence_id)
        logs = CustodyLog.objects.filter(
            evidence=selected_evidence
        ).select_related("performed_by", "case", "evidence").order_by("-timestamp")
    elif case_id:
        # Show all logs for this case
        logs = CustodyLog.objects.filter(
            case=selected_case
        ).select_related("performed_by", "case", "evidence").order_by("-timestamp")

    total_logs = logs.count() if logs else 0

    return render(
        request,
        "custody/timeline.html",
        {
            "cases": cases,
            "evidences": evidences,
            "selected_case": selected_case,
            "selected_evidence": selected_evidence,
            "logs": logs,
            "total_logs": total_logs,
        }
    )


@login_required
def integrity_console(request):

    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins are not allowed to access this page.")

    if user.profile.role != "AUDITOR":
        return HttpResponseForbidden("Access denied.")

    evidences = Evidence.objects.select_related("case").all()

    results = []
    total_checked = 0
    total_valid = 0
    total_compromised = 0
    scan_performed = False

    # Get last verification timestamp
    last_verify = CustodyLog.objects.filter(
        action_type="VERIFY"
    ).order_by("-timestamp").first()

    if request.method == "POST":
        scan_performed = True
        for evidence in evidences:

            is_valid = HashService.verify_hash(
                evidence.file,
                evidence.sha256_hash
            )

            CustodyLog.objects.create(
                case=evidence.case,
                evidence=evidence,
                performed_by=request.user,
                action_type="VERIFY",
                remarks="Integrity verified: VALID"
                        if is_valid
                        else "Integrity verified: COMPROMISED"
            )

            current_hash = HashService.generate_sha256(evidence.file)

            results.append({
                "evidence": evidence,
                "original_hash": evidence.sha256_hash,
                "current_hash": current_hash,
                "is_valid": is_valid,
            })

            total_checked += 1
            if is_valid:
                total_valid += 1
            else:
                total_compromised += 1

        return redirect(f"{request.path}?scanned=1")

    # On GET after redirect, show saved results from session? No — just show empty.
    # If scanned=1 param, re-compute results (idempotent read)
    if request.GET.get("scanned") == "1":
        scan_performed = True
        for evidence in evidences:
            current_hash = HashService.generate_sha256(evidence.file)
            is_valid = current_hash == evidence.sha256_hash

            results.append({
                "evidence": evidence,
                "original_hash": evidence.sha256_hash,
                "current_hash": current_hash,
                "is_valid": is_valid,
            })
            total_checked += 1
            if is_valid:
                total_valid += 1
            else:
                total_compromised += 1

    return render(
        request,
        "custody/integrity_console.html",
        {
            "results": results,
            "evidences": evidences,
            "total_checked": total_checked,
            "total_valid": total_valid,
            "total_compromised": total_compromised,
            "scan_performed": scan_performed,
            "last_verify": last_verify,
        }
    )


@login_required
def generate_report(request):

    user = request.user

    if user.is_superuser:
        return HttpResponseForbidden("Admins are not allowed to access this page.")

    if user.profile.role != "AUDITOR":
        return HttpResponseForbidden("Access denied.")

    cases = Case.objects.all().order_by("-created_at")

    selected_case = None
    evidences = None
    reference_id = None
    investigators = None
    custody_logs = None
    evidence_details = []
    action_summary = {}
    total_evidence_size = 0

    case_id = request.GET.get("case_id")

    if case_id:
        selected_case = get_object_or_404(Case, id=case_id)
        evidences = Evidence.objects.filter(case=selected_case).select_related("uploaded_by")

        reference_id = f"AUD-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"

        # Get investigators assigned to this case
        members = CaseMember.objects.filter(case=selected_case).select_related("user")
        investigators = [m.user for m in members]

        # Get all custody logs for this case, ordered by time
        custody_logs = CustodyLog.objects.filter(
            case=selected_case
        ).select_related("performed_by", "evidence").order_by("timestamp")

        # Action type summary counts
        action_counts = custody_logs.values("action_type").annotate(count=Count("action_type"))
        for item in action_counts:
            action_summary[item["action_type"]] = item["count"]

        # Build detailed evidence info with notes + integrity check
        for ev in evidences:
            notes = EvidenceNote.objects.filter(evidence=ev).select_related("author").order_by("created_at")
            current_hash = HashService.generate_sha256(ev.file)
            is_valid = current_hash == ev.sha256_hash
            total_evidence_size += ev.file_size

            evidence_details.append({
                "evidence": ev,
                "notes": notes,
                "current_hash": current_hash,
                "is_valid": is_valid,
            })

    return render(
        request,
        "custody/generate_report.html",
        {
            "cases": cases,
            "selected_case": selected_case,
            "evidences": evidences,
            "evidence_details": evidence_details,
            "reference_id": reference_id,
            "today": timezone.now(),
            "investigators": investigators,
            "custody_logs": custody_logs,
            "action_summary": action_summary,
            "total_evidence_size": total_evidence_size,
        }
    )