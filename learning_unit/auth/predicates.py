from django.utils.translation import gettext_lazy as _
from rules import predicate

from osis_role.errors import predicate_failed_msg


@predicate(bind=True)
@predicate_failed_msg(message=_("The user is not attached to the management entity"))
def is_user_attached_to_management_entity(self, user, education_group_year=None):
    if education_group_year:
        user_entity_ids = self.context['role_qs'].get_entities_ids()
        return education_group_year.management_entity_id in user_entity_ids
    return education_group_year
