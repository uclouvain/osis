############################################################################
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
############################################################################
from collections import OrderedDict

from django import forms
from django.forms import modelformset_factory
from django.utils.translation import ugettext_lazy as _

from base.forms.learning_unit.edition_volume import StepHalfIntegerWidget
from base.forms.utils.emptyfield import EmptyField
from base.models.entity_component_year import EntityComponentYear
from base.models.enums import entity_container_year_link_type as entity_types
from base.models.enums.component_type import DEFAULT_ACRONYM_COMPONENT, COMPONENT_TYPES
from base.models.enums.learning_container_year_types import CONTAINER_TYPE_WITH_DEFAULT_COMPONENT
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_component import LearningUnitComponent


class SimplifiedVolumeForm(forms.ModelForm):
    _learning_unit_year = None
    _entity_containers = []

    add_field = EmptyField(label="+")
    equal_field = EmptyField(label='=')

    def __init__(self, component_type, index, *args, is_faculty_manager=False, **kwargs):
        component_type = component_type
        self.is_faculty_manager = is_faculty_manager
        self.index = index
        super().__init__(*args, **kwargs)
        self.label = component_type[1]
        self.instance.type = component_type[0]
        self.instance.acronym = DEFAULT_ACRONYM_COMPONENT[self.instance.type]

    class Meta:
        model = LearningComponentYear
        fields = (
            'hourly_volume_total_annual',
            'hourly_volume_partial_q1',
            'hourly_volume_partial_q2'
        )
        widgets = {
            'hourly_volume_total_annual': StepHalfIntegerWidget,
            'hourly_volume_partial_q1': StepHalfIntegerWidget,
            'hourly_volume_partial_q2': StepHalfIntegerWidget,
        }

    def clean(self):
        """
        Prevent faculty users to a volume to 0 if there was a value other than 0.
        Also, prevent the faculty user from putting a volume if its value was 0.
        # FIXME Refactor this method with the clean of VolumeEditionForm
        """
        cleaned_data = super().clean()
        if self.is_faculty_manager:
            if 0 in [self.instance.hourly_volume_partial_q1, self.instance.hourly_volume_partial_q2]:
                if 0 not in [self.cleaned_data.get("hourly_volume_partial_q1"),
                             self.cleaned_data.get("hourly_volume_partial_q2")]:
                    self.add_error("hourly_volume_partial_q1", _("One of the partial volumes must have a value to 0."))
                    self.add_error("hourly_volume_partial_q2", _("One of the partial volumes must have a value to 0."))

            else:
                if self.cleaned_data.get("hourly_volume_partial_q1") == 0:
                    self.add_error("hourly_volume_partial_q1", _("The volume can not be set to 0."))
                if self.cleaned_data.get("hourly_volume_partial_q2") == 0:
                    self.add_error("hourly_volume_partial_q2", _("The volume can not be set to 0."))

        return cleaned_data

    def save(self, commit=True):
        if self.need_to_create_untyped_component():
            self.instance.acronym = DEFAULT_ACRONYM_COMPONENT[None]
            self.instance.type = None
            # In case of untyped component, we just need to create only 1 component (not more)
            if self.index != 0:
                return None
        return self._create_structure_components(commit)

    def need_to_create_untyped_component(self):
        container_type = self._learning_unit_year.learning_container_year.container_type
        return container_type not in CONTAINER_TYPE_WITH_DEFAULT_COMPONENT

    def _create_structure_components(self, commit):
        self.instance.learning_container_year = self._learning_unit_year.learning_container_year

        if self.instance.hourly_volume_total_annual is None or self.instance.hourly_volume_total_annual == 0:
            self.instance.planned_classes = 0
        else:
            self.instance.planned_classes = 1
        instance = super().save(commit)

        LearningUnitComponent.objects.update_or_create(
            learning_unit_year=self._learning_unit_year,
            learning_component_year=instance
        )

        requirement_entity_containers = self._get_requirement_entity_container()
        for requirement_entity_container in requirement_entity_containers:
            learning_unit_components = LearningUnitComponent.objects.filter(
                learning_unit_year__learning_container_year=self._learning_unit_year.learning_container_year
            )
            self._create_entity_component_years(learning_unit_components, requirement_entity_container)
        return instance

    def _create_entity_component_years(self, learning_unit_components, requirement_entity_container):
        for learning_unit_component in learning_unit_components:
            EntityComponentYear.objects.update_or_create(
                entity_container_year=requirement_entity_container,
                learning_component_year=learning_unit_component.learning_component_year
            )

    def _get_requirement_entity_container(self):
        requirement_entity_containers = []
        for entity_container_year in self._entity_containers:
            if entity_container_year and entity_container_year.type != entity_types.ALLOCATION_ENTITY:
                requirement_entity_containers.append(entity_container_year)
        return requirement_entity_containers


class SimplifiedVolumeFormset(forms.BaseModelFormSet):
    def __init__(self, data, person, *args, **kwargs):
        self.is_faculty_manager = person.is_faculty_manager() and not person.is_central_manager()
        super().__init__(data, *args, prefix="component", **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['component_type'] = COMPONENT_TYPES[index]
        kwargs['is_faculty_manager'] = self.is_faculty_manager
        kwargs['index'] = index
        return kwargs

    @property
    def fields(self):
        fields = OrderedDict()
        for form_instance in self.forms:
            fields.update({form_instance.add_prefix(name): field for name, field in form_instance.fields.items()})
        return fields

    @property
    def instances_data(self):
        data = {}
        zip_form_and_initial_forms = zip(self.forms, self.initial_forms)
        for form_instance, initial_form in zip_form_and_initial_forms:
            for col in ['hourly_volume_total_annual', 'hourly_volume_partial_q1', 'hourly_volume_partial_q2']:
                value = getattr(form_instance.instance, col, None) or getattr(initial_form.instance, col, None)
                data[_(form_instance.instance.type) + ' (' + self.label_fields[col].lower() + ')'] = value
        return data

    @property
    def label_fields(self):
        """ Return a dictionary with the label of all fields """
        data = {}
        for form_instance in self.forms:
            data.update({
                key: field.label for key, field in form_instance.fields.items()
            })
        return data

    def save_all_forms(self, learning_unit_year, entity_container_years, commit=True):
        for form in self.forms:
            form._learning_unit_year = learning_unit_year
            form._entity_containers = entity_container_years
        return super().save(commit)


SimplifiedVolumeManagementForm = modelformset_factory(
    model=LearningComponentYear,
    form=SimplifiedVolumeForm,
    formset=SimplifiedVolumeFormset,
    extra=2,
    max_num=2
)
