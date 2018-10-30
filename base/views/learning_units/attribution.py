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
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.business.learning_units import perms
from base.forms.learning_unit.attribution_charge_repartition import AttributionForm, LecturingAttributionChargeForm, \
    PracticalAttributionChargeForm
from base.models.enums import learning_component_year_type
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views.mixins import AjaxTemplateMixin, RulesRequiredMixin, MultiFormsView


class AttributionBaseViewMixin(RulesRequiredMixin):
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
        context["learning_unit_year"] = self.luy
        return context

    def get_success_url(self):
        return reverse("learning_unit_attributions", args=[self.kwargs["learning_unit_year_id"]])


class EditAttributionView(AttributionBaseViewMixin, AjaxTemplateMixin, MultiFormsView):
    rules = [perms.is_eligible_to_manage_attributions]
    template_name = "learning_unit/edit_attribution.html"
    form_classes = {
        "attribution_form": AttributionForm,
        "lecturing_charge_form": LecturingAttributionChargeForm,
        "practical_charge_form": PracticalAttributionChargeForm
    }
    prefixes = {
        "attribution_form": "attribution_form",
        "lecturing_charge_form": "lecturing_form",
        "practical_charge_form": "practical_form"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attribution"] = self.attribution
        return context

    def get_form_kwargs(self, form_name):
        form_kwargs = super().get_form_kwargs(form_name)
        form_kwargs.update({"instance": self.get_instance_form(form_name)})
        return form_kwargs

    def get_instance_form(self, form_name):
        return {
            "attribution_form": self.attribution,
            "lecturing_charge_form": self.attribution.lecturing_charges[0] if self.attribution.lecturing_charges
            else None,
            "practical_charge_form": self.attribution.practical_charges[0] if self.attribution.practical_charges
            else None
        }.get(form_name)

    def attribution_form_valid(self, form):
        form.save()

    def lecturing_charge_form_valid(self, form):
        form.save(self.attribution, self.luy)

    def practical_charge_form_valid(self, form):
        form.save(self.attribution, self.luy)

    def get_success_message(self, cleaned_data):
        return _("Attribution modified for %(tutor)s (%(function)s)") % {"tutor": self.attribution.tutor.person,
                                                                         "function": _(self.attribution.function)}


class DeleteAttribution(AttributionBaseViewMixin, AjaxTemplateMixin, SuccessMessageMixin, DeleteView):
    rules = [lambda luy, person: perms.is_eligible_to_manage_charge_repartition(luy, person)
                                 or perms.is_eligible_to_manage_attributions(luy, person)]
    model = AttributionNew
    template_name = "learning_unit/remove_charge_repartition_confirmation.html"
    pk_url_kwarg = "attribution_id"

    def delete(self, request, *args, **kwargs):
        delete_attribution(self.kwargs["attribution_id"])
        success_url = self.get_success_url()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attribution"] = self.attribution
        return context

    def get_success_message(self, cleaned_data):
        return _("Repartition removed for %(tutor)s (%(function)s)") % {"tutor": self.attribution.tutor.person,
                                                                        "function": _(self.attribution.function)}


def delete_attribution(attribution_pk):
    attribution_charges = AttributionChargeNew.objects.filter(attribution=attribution_pk)
    for charge in attribution_charges:
        charge.delete()

    AttributionNew.objects.get(pk=attribution_pk).delete()