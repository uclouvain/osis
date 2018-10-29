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
from django.forms import ModelForm, formset_factory, BaseFormSet, inlineformset_factory

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.models.enums import learning_component_year_type
from base.models.learning_component_year import LearningComponentYear


class AttributionForm(ModelForm):
    class Meta:
        model = AttributionNew
        fields = ["function", "start_year", "start_year"]


class AttributionChargeForm(ModelForm):
    class Meta:
        model = AttributionChargeNew
        fields = ["allocation_charge"]

    def save(self, attribution_new_obj, luy_obj, component_type):
        attribution_charge_obj = super().save(commit=False)

        learning_component_year = LearningComponentYear.objects.get(
            type=component_type,
            learningunitcomponent__learning_unit_year=luy_obj
        )

        attribution_charge_obj.attribution = attribution_new_obj
        attribution_charge_obj.learning_component_year = learning_component_year
        attribution_charge_obj.save()

        return attribution_charge_obj


class LecturingAttributionChargeForm(AttributionChargeForm):

    def save(self, attribution_new_obj, luy_obj):
        super().save(attribution_new_obj, luy_obj, learning_component_year_type.LECTURING)


class PracticalAttributionChargeForm(AttributionChargeForm):

    def save(self, attribution_new_obj, luy_obj):
        super().save(attribution_new_obj, luy_obj, learning_component_year_type.PRACTICAL_EXERCISES)


AttributionChargeRepartitionFormSet = formset_factory(AttributionChargeForm, max_num=2, min_num=2)


class AttributionChargeNewForm(ModelForm):
    class Meta:
        model = AttributionChargeNew
        fields = ["allocation_charge"]

    def save(self, attribution_new_obj, luy_obj, component_type):
        attribution_charge_obj = super().save(commit=False)

        learning_component_year = LearningComponentYear.objects.get(
            type=component_type,
            learningunitcomponent__learning_unit_year=luy_obj
        )

        attribution_charge_obj.attribution = attribution_new_obj
        attribution_charge_obj.learning_component_year = learning_component_year
        attribution_charge_obj.save()

        return attribution_charge_obj


class BaseAttributionChargeNewFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["instance"] = kwargs["instances"][index]
        del kwargs["instances"]
        return kwargs


AttributionChargeNewFormSet = formset_factory(AttributionChargeNewForm, formset=BaseAttributionChargeNewFormSet,
                                              max_num=2,
                                              min_num=2)
