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
from collections import OrderedDict

from django import forms
from django.db import transaction
from django.db.models import Prefetch
from django.forms import formset_factory
from django.utils.translation import ugettext_lazy as _

from base.business.learning_unit_year_with_context import ENTITY_TYPES_VOLUME
from base.business.learning_units import edition
from base.business.learning_units.edition import check_postponement_conflict_report_errors
from base.forms.common import STEP_HALF_INTEGER
from base.forms.utils.emptyfield import EmptyField
from base.models.entity_component_year import EntityComponentYear
from base.models.enums import entity_container_year_link_type as entity_types
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES_CANT_UPDATE_BY_FACULTY
from base.models.learning_unit_component import LearningUnitComponent


class StepHalfIntegerWidget(forms.NumberInput):
    def __init__(self):
        super().__init__(attrs={'step': STEP_HALF_INTEGER})


class VolumeField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_digits=6, decimal_places=2, min_value=0, **kwargs)


class VolumeEditionForm(forms.Form):
    requirement_entity_key = 'volume_' + entity_types.REQUIREMENT_ENTITY.lower()
    additional_requirement_entity_1_key = 'volume_' + entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1.lower()
    additional_requirement_entity_2_key = 'volume_' + entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2.lower()

    opening_parenthesis_field = EmptyField(label='(')
    volume_q1 = VolumeField(
        label=_('Q1'),
        help_text=_('Volume Q1'),
        widget=StepHalfIntegerWidget(),
    )
    add_field = EmptyField(label='+')
    volume_q2 = VolumeField(
        label=_('Q2'),
        help_text=_('Volume Q2'),
        widget=StepHalfIntegerWidget(),
    )
    equal_field_1 = EmptyField(label='=')
    volume_total = VolumeField(
        label=_('Vol. annual'),
        help_text=_('The annual volume must be equal to the sum of the volumes Q1 and Q2'),
        widget=StepHalfIntegerWidget(),
    )
    help_volume_total = "{} = {} + {}".format(_('Volume total annual'), _('Volume Q1'), _('Volume Q2'))
    closing_parenthesis_field = EmptyField(label=')')
    mult_field = EmptyField(label='*')
    planned_classes = forms.IntegerField(label=_('P.C.'), help_text=_('Planned classes'), min_value=0)
    equal_field_2 = EmptyField(label='=')

    _post_errors = []
    _parent_data = {}
    _faculty_manager_fields = ['volume_q1', 'volume_q2']

    def __init__(self, *args, **kwargs):
        self.component = kwargs.pop('component')
        self.learning_unit_year = kwargs.pop('learning_unit_year')
        self.entities = kwargs.pop('entities', [])
        self.is_faculty_manager = kwargs.pop('is_faculty_manager', False)

        self.title = self.component.acronym
        self.title_help = _(self.component.type) + ' ' if self.component.type else ''
        self.title_help += self.component.acronym

        super().__init__(*args, **kwargs)
        help_volume_global = "{} = {} * {}".format(_('volume total global'),
                                                   _('Volume total annual'),
                                                   _('Planned classes'))

        # Append dynamic fields
        entities_to_add = [entity for entity in ENTITY_TYPES_VOLUME if entity in self.entities]
        for i, key in enumerate(entities_to_add):
            entity = self.entities[key]
            self.fields["volume_" + key.lower()] = VolumeField(
                label=entity.acronym,
                help_text=entity.title,
                widget=StepHalfIntegerWidget(),
            )
            if i != len(entities_to_add) - 1:
                self.fields["add" + key.lower()] = EmptyField(label='+')

        if self.is_faculty_manager \
                and self.learning_unit_year.is_full() \
                and self.learning_unit_year.learning_container_year.container_type \
                in LEARNING_CONTAINER_YEAR_TYPES_CANT_UPDATE_BY_FACULTY:
            self._disable_central_manager_fields()

    def _disable_central_manager_fields(self):
        for key, field in self.fields.items():
            if key not in self._faculty_manager_fields:
                field.disabled = True

    def clean(self):
        """
        Prevent faculty users to a volume to 0 if there was a value other than 0.
        Also, prevent the faculty user from putting a volume if its value was 0.
        """
        cleaned_data = super().clean()

        if self.is_faculty_manager:

            if 0 in [self.initial.get("volume_q1"), self.initial.get("volume_q2")]:
                if 0 not in [self.cleaned_data.get("volume_q1"), self.cleaned_data.get("volume_q2")]:
                    self.add_error("volume_q1", _("One of the partial volumes must have a value to 0."))
                    self.add_error("volume_q2", _("One of the partial volumes must have a value to 0."))

            else:
                if self.cleaned_data.get("volume_q1") == 0:
                    self.add_error("volume_q1", _("The volume can not be set to 0."))
                if self.cleaned_data.get("volume_q2") == 0:
                    self.add_error("volume_q2", _("The volume can not be set to 0."))

        return cleaned_data

    def get_entity_fields(self):
        entity_keys = [self.requirement_entity_key, self.additional_requirement_entity_1_key,
                       self.additional_requirement_entity_2_key]
        return [self.fields[key] for key in entity_keys if key in self.fields]

    def save(self, postponement):
        if not self.changed_data:
            return None

        conflict_report = {}
        if postponement:
            conflict_report = edition.get_postponement_conflict_report(self.learning_unit_year)
            luy_to_update_list = conflict_report['luy_without_conflict']
        else:
            luy_to_update_list = [self.learning_unit_year]

        with transaction.atomic():
            for component in self._find_learning_components_year(luy_to_update_list):
                self._save(component)

        # Show conflict error if exists
        check_postponement_conflict_report_errors(conflict_report)

    def _save(self, component):
        component.hourly_volume_total_annual = self.cleaned_data['volume_total']
        component.hourly_volume_partial_q1 = self.cleaned_data['volume_q1']
        component.hourly_volume_partial_q2 = self.cleaned_data['volume_q2']
        component.planned_classes = self.cleaned_data['planned_classes']
        component.save()
        self._save_requirement_entities(component.entity_components_year)

    def _save_requirement_entities(self, entity_components_year):
        for ecy in entity_components_year:
            link_type = ecy.entity_container_year.type
            repartition_volume = self.cleaned_data.get('volume_' + link_type.lower())

            if repartition_volume is None:
                continue

            ecy.repartition_volume = repartition_volume
            ecy.save()

    def _find_learning_components_year(self, luy_to_update_list):
        prefetch = Prefetch(
            'learning_component_year__entitycomponentyear_set',
            queryset=EntityComponentYear.objects.all(),
            to_attr='entity_components_year'
        )
        return [
            luc.learning_component_year
            for luc in LearningUnitComponent.objects.filter(
                learning_unit_year__in=luy_to_update_list).prefetch_related(prefetch)
            if luc.learning_component_year.type == self.component.type
        ]


class VolumeEditionBaseFormset(forms.BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year')
        self.components = list(self.learning_unit_year.components.keys())
        self.components_values = list(self.learning_unit_year.components.values())
        self.is_faculty_manager = kwargs.pop('is_faculty_manager')

        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['learning_unit_year'] = self.learning_unit_year
        kwargs['component'] = self.components[index]
        kwargs['initial'] = self._clean_component_keys(self.components_values[index])
        kwargs['entities'] = self.learning_unit_year.entities
        kwargs['is_faculty_manager'] = self.is_faculty_manager
        return kwargs

    @staticmethod
    def _clean_component_keys(component_dict):
        # Field's name must be in lowercase
        return {k.lower(): v for k, v in component_dict.items()}

    def save(self, postponement):
        for form in self.forms:
            form.save(postponement)


class VolumeEditionFormsetContainer:
    """
    Create and Manage a set of VolumeEditionFormsets
    """

    def __init__(self, request, learning_units, person):
        self.formsets = OrderedDict()
        self.learning_units = learning_units
        self.parent = self.learning_units[0]
        self.postponement = int(request.POST.get('postponement', 1))
        self.request = request

        self.is_faculty_manager = person.is_faculty_manager() and not person.is_central_manager()

        for learning_unit in learning_units:
            volume_edition_formset = formset_factory(
                form=VolumeEditionForm, formset=VolumeEditionBaseFormset, extra=len(learning_unit.components)
            )
            self.formsets[learning_unit] = volume_edition_formset(
                request.POST or None,
                learning_unit_year=learning_unit,
                prefix=learning_unit.acronym,
                is_faculty_manager=self.is_faculty_manager
            )

    def is_valid(self):
        if not self.request.POST:
            return False

        if not all([formset.is_valid() for formset in self.formsets.values()]):
            return False

        return True

    def save(self):
        for formset in self.formsets.values():
            formset.save(self.postponement)

    @property
    def errors(self):
        errors = {}
        for formset in self.formsets.values():
            errors.update(self._get_formset_errors(formset))
        return errors

    @staticmethod
    def _get_formset_errors(formset):
        errors = {}
        for i, form_errors in enumerate(formset.errors):
            for name, error in form_errors.items():
                errors["{}-{}-{}".format(formset.prefix, i, name)] = error
        return errors
