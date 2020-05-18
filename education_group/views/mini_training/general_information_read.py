import functools

from django.urls import reverse

from base.business.education_groups import general_information_sections
from base.models.enums.publication_contact_type import PublicationContactType
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
                self.request.user.has_perm("base.change_pedagogyinformation", self.get_education_group_version().offer),
            "show_contacts": self.can_have_contacts(),
            "entity_contact": self.get_entity_contact(),
            "academic_responsibles": self.get_academic_responsibles(),
            "other_academic_responsibles": self.get_other_academic_responsibles(),
            "jury_members": self.get_jury_members(),
            "other_contacts": self.get_other_contacts()
        }

    def get_sections(self):
        return serializers.general_information.get_sections(self.get_object(), self.request.LANGUAGE_CODE)

    def can_have_contacts(self):
        node = self.get_object()
        return general_information_sections.CONTACTS in \
            general_information_sections.SECTIONS_PER_OFFER_TYPE[node.category.name]['specific']

    def get_entity_contact(self):
        return getattr(
            self.get_education_group_version().offer.publication_contact_entity_version,
            'verbose_title',
            None
        )

    def get_academic_responsibles(self):
        return self._get_contacts().get(PublicationContactType.ACADEMIC_RESPONSIBLE.name) or []

    def get_other_academic_responsibles(self):
        return self._get_contacts().get(PublicationContactType.OTHER_ACADEMIC_RESPONSIBLE.name) or []

    def get_jury_members(self):
        return self._get_contacts().get(PublicationContactType.JURY_MEMBER.name) or []

    def get_other_contacts(self):
        return self._get_contacts().get(PublicationContactType.OTHER_CONTACT.name) or []

    @functools.lru_cache()
    def _get_contacts(self):
        return serializers.general_information.get_contacts(self.get_object())
