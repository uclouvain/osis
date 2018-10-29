##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.business.learning_units import perms
from base.forms.learning_unit.attribution_charge_repartition import AttributionChargeRepartitionFormSet, \
    AttributionChargeNewFormSet, LecturingAttributionChargeForm, PracticalAttributionChargeForm
from base.models.enums import learning_component_year_type
from base.models.learning_unit_component import LearningUnitComponent
from base.views.learning_units.attribution import AttributionBaseViewMixin, EditAttributionView
from base.views.mixins import AjaxTemplateMixin


class SelectAttributionView(AttributionBaseViewMixin, TemplateView):
    template_name = "learning_unit/select_attribution.html"

    @cached_property
    def attributions(self):
        lecturing_charges = AttributionChargeNew.objects \
            .filter(learning_component_year__type=learning_component_year_type.LECTURING)
        prefetch_lecturing_charges = Prefetch("attributionchargenew_set", queryset=lecturing_charges,
                                              to_attr="lecturing_charges")

        practical_charges = AttributionChargeNew.objects \
            .filter(learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES)
        prefetch_practical_charges = Prefetch("attributionchargenew_set", queryset=practical_charges,
                                              to_attr="practical_charges")
        attributions_to_exclude = AttributionChargeNew.objects \
            .filter(learning_component_year__learningunitcomponent__learning_unit_year=self.luy) \
            .annotate(id_text=Concat("attribution__tutor__person__global_id", "attribution__function")) \
            .values_list("id_text", flat=True)

        parent_luc = LearningUnitComponent.objects.filter(learning_unit_year=self.parent_luy)
        parent_attributions = AttributionNew.objects \
            .filter(attributionchargenew__learning_component_year__learningunitcomponent__in=parent_luc) \
            .distinct("id") \
            .annotate(id_text=Concat("tutor__person__global_id", "function")) \
            .exclude(id_text__in=attributions_to_exclude) \
            .prefetch_related(prefetch_lecturing_charges) \
            .prefetch_related(prefetch_practical_charges) \
            .select_related("tutor__person")
        return parent_attributions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attributions"] = self.attributions
        return context


class AddChargeRepartition(AttributionBaseViewMixin, AjaxTemplateMixin, SuccessMessageMixin, FormView):
    template_name = "learning_unit/add_charge_repartition.html"
    form_class = AttributionChargeRepartitionFormSet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = context["form"]
        context["attribution"] = self.attribution
        return context

    def get_initial(self):
        lecturing_allocation_charge = self.attribution.lecturing_charges[0].allocation_charge \
            if self.attribution.lecturing_charges else None
        practical_allocation_charge = self.attribution.practical_charges[0].allocation_charge \
            if self.attribution.practical_charges else None
        initial_data = [
            {"allocation_charge": lecturing_allocation_charge},
            {"allocation_charge": practical_allocation_charge}
        ]
        return initial_data

    def form_valid(self, formset):
        attribution_copy = self.attribution
        attribution_copy.id = None
        attribution_copy.save()

        types = (learning_component_year_type.LECTURING, learning_component_year_type.PRACTICAL_EXERCISES)
        for form, component_type in zip(formset, types):
            form.save(attribution_copy, self.luy, component_type)

        return super().form_valid(formset)

    def get_success_message(self, cleaned_data):
        return _("Repartition added for %(tutor)s (%(function)s)") % {"tutor": self.attribution.tutor.person,
                                                                      "function": _(self.attribution.function)}


class EditChargeRepartition(EditAttributionView):
    rules = [perms.is_eligible_to_manage_charge_repartition]
    template_name = "learning_unit/add_charge_repartition.html"
    form_classes = {
        "lecturing_charge_form": LecturingAttributionChargeForm,
        "practical_charge_form": PracticalAttributionChargeForm
    }

    def forms_valid(self, forms):
        lecturing_charge_form = forms["lecturing_charge_form"]
        practical_charge_form = forms["practical_charge_form"]

        for form in (lecturing_charge_form, practical_charge_form):
            form.save(self.attribution, self.luy)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_message(self, cleaned_data):
        return _("Repartition modified for %(tutor)s (%(function)s)") % {"tutor": self.attribution.tutor.person,
                                                                         "function": _(self.attribution.function)}
