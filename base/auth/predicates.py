from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rules import predicate

from base.models.education_group_year import EducationGroupYear
from osis_role.errors import predicate_failed_msg


@predicate(bind=True)
@predicate_failed_msg(message=_("The user is not linked to this offer"))
def is_linked_to_offer(self, user: User, egy: EducationGroupYear):
    if egy:
        return any(
            egy.education_group.pk in role.get_person_related_education_groups(role.person)
            for role in self.context['role_qs']
        )
    return None
