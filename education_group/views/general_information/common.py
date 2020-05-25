from enum import Enum

from django.urls import reverse
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

from base.models.education_group_year import EducationGroupYear
from education_group.views.serializers import general_information
from osis_role.contrib.views import PermissionRequiredMixin


class Tab(Enum):
    GENERAL_INFO = 0


class CommonGeneralInformation(PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = 'base.view_educationgroup'
    raise_exception = True
    template_name = "general_information/common.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "object": self.get_object(),
            "tab_urls": self.get_tab_urls(),
            "sections": self.get_sections(),
            "update_label_url": self.get_update_label_url(),
            "can_edit_information": self.request.user.has_perm(
                "base.change_commonpedagogyinformation", self.get_object()
            )
        }

    def get_tab_urls(self):
        return {
             Tab.GENERAL_INFO: {
                'text': _('General informations'),
                'active': True,
                'display': True,
                'url': reverse('common_general_information', kwargs={'year': self.kwargs['year']})
             }
        }

    def get_sections(self):
        return general_information.get_sections_of_common(self.kwargs['year'], self.request.LANGUAGE_CODE)

    def get_object(self):
        return EducationGroupYear.objects.get_common(academic_year__year=self.kwargs['year'])

    def get_update_label_url(self):
        offer_id = self.get_object().pk
        return reverse('education_group_pedagogy_edit', args=[offer_id, offer_id])
