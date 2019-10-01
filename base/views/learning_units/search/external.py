from django.contrib.auth.mixins import PermissionRequiredMixin
from django_filters.views import FilterView

from base.forms.learning_unit.search.external import ExternalLearningUnitFilter
from base.models.academic_year import starting_academic_year
from base.models.learning_unit_year import LearningUnitYear
from base.templatetags import pagination
from base.utils.cache import CacheFilterMixin
from base.views.learning_units.search.common import EXTERNAL_SEARCH, SerializeFilterListIfAjaxMixin
from learning_unit.api.serializers.learning_unit import LearningUnitDetailedSerializer


class ExternalLearningUnitSearch(PermissionRequiredMixin, CacheFilterMixin, SerializeFilterListIfAjaxMixin, FilterView):
    model = LearningUnitYear
    template_name = "learning_unit/search/external.html"
    raise_exception = True
    search_type = EXTERNAL_SEARCH

    filterset_class = ExternalLearningUnitFilter
    permission_required = 'base.can_access_externallearningunityear'

    serializer_class = LearningUnitDetailedSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        starting_ac = starting_academic_year()

        context.update({
            'form': context['filter'].form,
            'learning_units_count': context["paginator"].count,
            'current_academic_year': starting_ac,
            'proposal_academic_year': starting_ac.next(),
            'search_type': self.search_type,
            'page_obj': context["page_obj"],
            'items_per_page': context["paginator"].per_page,
        })
        return context

    def get_paginate_by(self, queryset):
        pagination.store_paginator_size(self.request)
        return pagination.get_paginator_size(self.request)
