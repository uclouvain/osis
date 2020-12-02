############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
############################################################################
from dal import autocomplete
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from attribution.forms.repartition_charge import AttributionChargeForm
from attribution.models.attribution_new import AttributionNew
from attribution.models.enums.function import Functions
from base.models.enums import learning_container_year_types, learning_component_year_type
from base.models.person import Person
from base.models.tutor import Tutor


class AttributionForm(forms.ModelForm):
    duration = forms.IntegerField(min_value=1, required=True, label=_("Duration"))

    class Meta:
        model = AttributionNew
        fields = ["function", "start_year"]

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop("learning_unit_year")
        super().__init__(*args, **kwargs)

        if self.learning_unit_year.learning_container_year.container_type != learning_container_year_types.COURSE or \
                self.learning_unit_year.is_partim():
            del self.fields["start_year"]
            del self.fields["duration"]
            self.fields["function"].choices = Functions.choices_without_professor()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.learning_unit_year.learning_container_year.container_type == learning_container_year_types.COURSE and \
                not self.learning_unit_year.is_partim():
            instance.end_year = instance.start_year + self.cleaned_data["duration"] - 1

        if commit:
            instance.save()
        return instance


class AttributionCreationForm(AttributionForm):
    person = forms.ModelChoiceField(
        queryset=Person.employees.all(),
        required=True,
        widget=autocomplete.ModelSelect2(
            url='employee_autocomplete',
            attrs={
                'data-theme': 'bootstrap',
                'data-placeholder': _('Indicate the name or the FGS'),
            }
        ),
        label='',
    )

    class Meta:
        model = AttributionNew
        fields = ["person", "function", "start_year"]

    class Media:
        css = {
            'all': ('css/select2-bootstrap.css',)
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.learning_container_year = self.learning_unit_year.learning_container_year
        tutor, _ = Tutor.objects.get_or_create(person=self.cleaned_data["person"])
        instance.tutor = tutor
        if commit:
            instance.save()
        return instance


def _get_formatted_label(label, abbr):
    return mark_safe('<abbr title="{}">{}</abbr>'.format(_(label), abbr))


class LecturingAttributionChargeForm(AttributionChargeForm):
    component_type = learning_component_year_type.LECTURING

    class Meta(AttributionChargeForm.Meta):
        labels = {
            'allocation_charge': _get_formatted_label('Lecturing', 'PM'),
        }


class PracticalAttributionChargeForm(AttributionChargeForm):
    component_type = learning_component_year_type.PRACTICAL_EXERCISES

    class Meta(AttributionChargeForm.Meta):
        labels = {
            'allocation_charge': _get_formatted_label('Practical exercises', 'PP')
        }
