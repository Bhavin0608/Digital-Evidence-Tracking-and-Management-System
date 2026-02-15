from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from cases.models import Case
from .models import Evidence
from .forms import EvidenceUploadForm
from core.hash_service import HashService


@login_required
def upload_evidence(request, case_id):

    case = get_object_or_404(Case, id=case_id)

    # ===== RBAC CHECK (Temporary Basic Check) =====
    if not request.user.is_superuser and case.assigned_senior_officer != request.user:
        if not case.members.filter(user=request.user).exists():
            return HttpResponseForbidden("You are not assigned to this case.")

    if request.method == "POST":
        form = EvidenceUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]

            sha256_hash = HashService.generate_sha256(file)

            evidence = Evidence.objects.create(
                case=case,
                file=file,
                file_name=file.name,
                file_type=file.name.split('.')[-1],
                file_size=file.size,
                sha256_hash=sha256_hash,
                uploaded_by=request.user
            )

            # CustodyLog will be added later

            return redirect("case_detail", case_id=case.id)

    else:
        form = EvidenceUploadForm()

    return render(request, "evidence/upload.html", {
        "form": form,
        "case": case
    })
