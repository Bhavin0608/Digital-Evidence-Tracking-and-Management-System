from cases.models import CaseMember


class RBACService:

    @staticmethod
    def can_access_case(user, case):

        if user.is_superuser:
            return True

        if not hasattr(user, "profile"):
            return False

        # Auditor can access all cases (read-only role)
        if user.profile.role == "AUDITOR":
            return True

        if case.assigned_so == user:
            return True

        if CaseMember.objects.filter(case=case, user=user).exists():
            return True

        return False

    @staticmethod
    def can_upload_evidence(user, case):
        """
        Only assigned investigators (or superuser) can upload evidence.
        """

        if user.is_superuser:
            return True

        # Must be assigned investigator
        return CaseMember.objects.filter(case=case, user=user).exists()

    @staticmethod
    def can_modify_evidence(user, evidence):
        """
        Only uploader (or superuser) can modify evidence.
        """

        if user.is_superuser:
            return True

        return evidence.uploaded_by == user