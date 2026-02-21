from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Case
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