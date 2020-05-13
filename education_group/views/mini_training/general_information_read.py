from django.urls import reverse

from education_group.views import serializers
from education_group.views.mini_training.common_read import MiniTrainingRead, Tab


class MiniTrainingReadGeneralInformation(MiniTrainingRead):
    template_name = "mini_training/general_informations_read.html"
    active_tab = Tab.GENERAL_INFO

    def get_context_data(self, **kwargs):
        node = self.get_object()
        return {
            **super().get_context_data(**kwargs),
            "sections": self.get_sections(),
            "publish_url": reverse('publish_general_information', args=[node.year, node.code]) +
            "?path={}".format(self.get_path()),
            "can_edit_information":
                self.request.user.has_perm("base.change_pedagogyinformation", self.get_education_group_version().offer)
        }

    def get_sections(self):
        return serializers.general_information.get_sections(self.get_object(), self.request.LANGUAGE_CODE)
