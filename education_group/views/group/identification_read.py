from reversion.models import Version

from education_group.models.group_year import GroupYear
from education_group.views.group.common_read import Tab, GroupRead


class GroupReadIdentification(GroupRead):
    template_name = "group/identification_read.html"
    active_tab = Tab.IDENTIFICATION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "history": self.get_related_history(),
        }

    def get_related_history(self):
        group_year = self.get_group_year()
        versions = Version.objects.get_for_object(
            group_year
        ).select_related('revision__user__person')

        related_models = [
            GroupYear,
        ]

        subversion = Version.objects.none()
        for model in related_models:
            subversion |= Version.objects.get_for_model(model).select_related('revision__user__person')

        versions |= subversion.filter(
            serialized_data__contains="\"group_year\": {}".format(group_year.pk)
        )

        return versions.order_by('-revision__date_created').distinct('revision__date_created')
