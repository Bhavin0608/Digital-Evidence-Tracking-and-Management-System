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
        extra_context["recent_logs"] = (
            CustodyLog.objects
            .select_related("case", "evidence", "performed_by")
            .order_by("-timestamp")[:10]
        )
        return super().index(request, extra_context=extra_context)
