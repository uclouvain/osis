from django.urls import reverse

from education_group.views import serializers
from education_group.views.group.common_read import Tab, GroupRead


class GroupReadGeneralInformation(GroupRead):
    template_name = "group/general_informations_read.html"
    active_tab = Tab.GENERAL_INFO

    def get_context_data(self, **kwargs):
        node = self.get_object()
        return {
            **super().get_context_data(**kwargs),
            "sections": self.get_sections(),
            "update_pedagocical_information_url": self.get_update_pedagocical_information_url(),
            "publish_url": reverse('publish_general_information', args=[node.year, node.code]) +
            "?path={}".format(self.path),
            "can_edit_information": self.request.user.has_perm("base.change_pedagogyinformation", self.get_group_year())
        }

    def get_sections(self):
        return serializers.general_information.get_sections(self.get_object(), self.request.LANGUAGE_CODE)

    def get_update_pedagocical_information_url(self):
        offer_id = self.get_group_year().pk
        return reverse('education_group_pedagogy_edit', args=[offer_id, offer_id])
