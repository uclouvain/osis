from django.utils import timezone

from dal import autocomplete

from base.models.entity_version import EntityVersion
from osis_role import role
from osis_role.contrib.models import EntityRoleModel


class EntityRoleAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete which allow to display entities which have a link with entity according to all EntityRoleModel
    declared in OSIS Role Manager
    """
    def __init__(self, group_names, **kwargs):
        assert not isinstance(group_names, tuple), "group_names kwargs must be an instance of tuple"
        self.group_names = group_names
        super().__init__(**kwargs)

    def get_queryset(self):
        entities_link_to_user = self._get_entites_linked_to_user()
        date = timezone.now()
        return EntityVersion.objects.current(date).filter(entity__in=entities_link_to_user)

    def _get_entites_linked_to_user(self):
        role_mdls = filter(
            lambda role: role.group_name in self.group_names and isinstance(role, EntityRoleModel),
            role.role_manager.group_names_managed()
        )

        qs = None
        for role_mdl in role_mdls:
            subqs = role_mdl.objects.filter(person=self.request.user.person).values('entity_id', 'with_children')
            if qs is None:
                qs = subqs
            else:
                qs.union(subqs)
        return qs.get_entities_ids()
