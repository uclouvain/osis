from enum import Enum

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import TrainingType
from osis_role.contrib.views import PermissionRequiredMixin


class Tab(Enum):
    ADMISSION_CONDITION = 0


class CommonAggregateAdmissionCondition(PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = 'base.view_educationgroup'
    raise_exception = True
    template_name = "general_information/common_aggregate.html"

    def get_context_data(self, **kwargs):
        object = self.get_object()
        return {
            **super().get_context_data(**kwargs),
            "object": object,
            "admission_condition": object.admissioncondition,
            "tab_urls": self.get_tab_urls(),
            "can_edit_information": self.request.user.has_perm(
                "base.change_commonadmissioncondition", self.get_object()
            )
        }

    def get_tab_urls(self):
        return {
            Tab.ADMISSION_CONDITION: {
                'text': _('Conditions'),
                'active': True,
                'display': True,
                'url': reverse('common_aggregate_admission_condition', kwargs={'year': self.kwargs['year']})
            }
        }

    def get_object(self) -> EducationGroupYear:
        try:
            return EducationGroupYear.objects.look_for_common(
                academic_year__year=self.kwargs['year'],
                education_group_type__name=TrainingType.AGGREGATION.name,
                admissioncondition__isnull=False
            ).select_related('admissioncondition').get()
        except EducationGroupYear.DoesNotExist:
            raise Http404
