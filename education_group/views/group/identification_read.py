from reversion.models import Version

from education_group.views.group.common_read import Tab, GroupRead


class GroupReadIdentification(GroupRead):
    template_name = "group/identification_read.html"
    active_tab = Tab.IDENTIFICATION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "versions": self.get_related_versions(),
        }

    def get_related_versions(self):
        return Version.objects.none()
