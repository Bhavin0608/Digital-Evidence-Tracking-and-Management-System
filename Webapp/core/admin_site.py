from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from cases.models import Case
from evidence.models import Evidence
from custody.models import CustodyLog


class DETAMSAdminSite(AdminSite):
    site_header = "DETAMS Administration"
    site_title = "DETAMS Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["total_cases"] = Case.objects.count()
        extra_context["total_officers"] = User.objects.filter(
            is_superuser=False
        ).count()
        extra_context["total_evidence"] = Evidence.objects.count()
        extra_context["total_logs"] = CustodyLog.objects.count()

        logs_qs = (
            CustodyLog.objects
            .select_related("case", "evidence", "performed_by")
            .order_by("-timestamp")
        )

        filter_case_id = request.GET.get("case")
        if filter_case_id:
            logs_qs = logs_qs.filter(case__id=filter_case_id)
        extra_context["recent_logs"] = logs_qs[:20]
        extra_context["all_cases"] = Case.objects.order_by("case_id")
        extra_context["selected_case"] = filter_case_id or ""

        return super().index(request, extra_context=extra_context)
