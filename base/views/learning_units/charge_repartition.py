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
import itertools

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, DeleteView
from django.views.generic.base import TemplateView

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.business.learning_units import perms
from base.forms.learning_unit.attribution_charge_repartition import AttributionChargeRepartitionFormSet, \
    AttributionChargeNewFormSet
from base.models.enums import learning_component_year_type
from base.models.learning_unit_component import LearningUnitComponent
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views.mixins import AjaxTemplateMixin, RulesRequiredMixin


class ChargeRepartitionBaseViewMixin(RulesRequiredMixin):
    rules = [perms.is_eligible_to_manage_charge_repartition]

    def _call_rule(self, rule):
        return rule(self.luy, get_object_or_404(Person, user=self.request.user))

    @cached_property
    def luy(self):
        return get_object_or_404(LearningUnitYear, id=self.kwargs["learning_unit_year_id"])

    @cached_property
    def parent_luy(self):
        return self.luy.parent

    @cached_property
    def attributions(self):
        lecturing_charges = AttributionChargeNew.objects\
            .filter(learning_component_year__type=learning_component_year_type.LECTURING)
        prefetch_lecturing_charges  = Prefetch("attributionchargenew_set", queryset=lecturing_charges,
                                               to_attr="lecturing_charges")

        practical_charges = AttributionChargeNew.objects\
            .filter(learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES)
        prefetch_practical_charges = Prefetch("attributionchargenew_set", queryset=practical_charges,
                                              to_attr="practical_charges")

        learning_unit_components = LearningUnitComponent.objects.filter(learning_unit_year=self.parent_luy)
        attributions = AttributionNew.objects\
            .filter(attributionchargenew__learning_component_year__learningunitcomponent__in=learning_unit_components)\
            .distinct("id")\
            .prefetch_related(prefetch_lecturing_charges)\
            .prefetch_related(prefetch_practical_charges)\
            .select_related("tutor__person")
        return attributions


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["learning_unit_year"] = self.luy
        context["attributions"] = self.attributions
        return context

    def get_success_url(self):
        return reverse("learning_unit_attributions", args=[self.kwargs["learning_unit_year_id"]])


class SelectAttributionView(ChargeRepartitionBaseViewMixin, TemplateView):
    template_name = "learning_unit/select_attribution.html"


class AddChargeRepartition(ChargeRepartitionBaseViewMixin, AjaxTemplateMixin, SuccessMessageMixin, FormView):
    template_name = "learning_unit/add_charge_repartition.html"
    form_class = AttributionChargeRepartitionFormSet
    success_message = _("Repartition added")

    @cached_property
    def attribution(self):
        lecturing_charges = AttributionChargeNew.objects \
            .filter(learning_component_year__type=learning_component_year_type.LECTURING)
        prefetch_lecturing_charges = Prefetch("attributionchargenew_set", queryset=lecturing_charges,
                                              to_attr="lecturing_charges")

        practical_charges = AttributionChargeNew.objects \
            .filter(learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES)
        prefetch_practical_charges = Prefetch("attributionchargenew_set", queryset=practical_charges,
                                              to_attr="practical_charges")

        attribution = AttributionNew.objects \
            .prefetch_related(prefetch_lecturing_charges) \
            .prefetch_related(prefetch_practical_charges) \
            .select_related("tutor__person") \
            .get(id=self.kwargs["attribution_id"])
        return attribution

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = context["form"]
        context["attribution"] = self.attribution
        return context

    def get_initial(self):
        lecturing_allocation_charge = self.attribution.lecturing_charges[0].allocation_charge
        practical_allocation_charge = self.attribution.practical_charges[0].allocation_charge
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


class EditChargeRepartition(ChargeRepartitionBaseViewMixin, AjaxTemplateMixin, SuccessMessageMixin, FormView):
    template_name = "learning_unit/add_charge_repartition.html"
    form_class = AttributionChargeNewFormSet
    success_message = _("Repartition edited")

    @cached_property
    def attribution(self):
        lecturing_charges = AttributionChargeNew.objects \
            .filter(learning_component_year__type=learning_component_year_type.LECTURING)
        prefetch_lecturing_charges = Prefetch("attributionchargenew_set", queryset=lecturing_charges,
                                              to_attr="lecturing_charges")

        practical_charges = AttributionChargeNew.objects \
            .filter(learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES)
        prefetch_practical_charges = Prefetch("attributionchargenew_set", queryset=practical_charges,
                                              to_attr="practical_charges")

        attribution = AttributionNew.objects \
            .prefetch_related(prefetch_lecturing_charges) \
            .prefetch_related(prefetch_practical_charges) \
            .select_related("tutor__person") \
            .get(id=self.kwargs["attribution_id"])
        return attribution

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = context["form"]
        context["attribution"] = self.attribution
        return context

    def get_form_kwargs(self):
        lecturing_charge = self.attribution.lecturing_charges[0]
        practical_charge = self.attribution.practical_charges[0]
        form_kwargs = super().get_form_kwargs()
        form_kwargs["form_kwargs"] = {
            "instances": [lecturing_charge, practical_charge]
        }
        return form_kwargs

    def form_valid(self, formset):
        for form in formset:
            form.save()
        return super().form_valid(formset)


class RemoveChargeRepartition(ChargeRepartitionBaseViewMixin, AjaxTemplateMixin, SuccessMessageMixin, DeleteView):
    model = AttributionNew
    template_name = "learning_unit/remove_charge_repartition_confirmation.html"
    pk_url_kwarg = "attribution_id"
    success_message = _("Repartition removed")

    @cached_property
    def attribution(self):
        return AttributionNew.objects \
            .select_related("tutor__person") \
            .get(id=self.kwargs["attribution_id"])

    def delete(self, request, *args, **kwargs):
        delete_attribution(self.kwargs["attribution_id"])
        success_url = self.get_success_url()
        # TODO check why no messages
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attribution"] = self.attribution
        return context


def delete_attribution(attribution_pk):
    attribution_charges = AttributionChargeNew.objects.filter(attribution=attribution_pk)
    for charge in attribution_charges:
        charge.delete()

    AttributionNew.objects.get(pk=attribution_pk).delete()
