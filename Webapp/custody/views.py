from django.http import HttpResponseForbidden
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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