from cases.models import CaseMember


class RBACService:

    @staticmethod
    def can_access_case(user, case):
        """
        General case access check.
        """
        if user.is_superuser:
            return True

        # Senior Officer access
        if case.assigned_senior_officer == user:
            return True

        # Investigator access
        if CaseMember.objects.filter(case=case, user=user).exists():
            return True

        return False

    @staticmethod
    def can_upload_evidence(user, case):
        """
        Only investigators assigned to case or superuser.
        """
        if user.is_superuser:
            return True

        return CaseMember.objects.filter(case=case, user=user).exists()

    @staticmethod
    def can_modify_evidence(user, evidence):
        """
        Only uploader or superuser can modify evidence.
        """
        if user.is_superuser:
            return True

        return evidence.uploaded_by == user
