from cases.models import CaseMember


class RBACService:

    @staticmethod
    def can_access_case(user, case):
        """
        General case access check.
        """

        # Admin full access
        if user.is_superuser:
            return True

        # Senior Officer assigned to case
        if case.assigned_so == user:
            return True

        # Investigator assigned via CaseMember
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