##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from collections.__init__ import OrderedDict

from dal import autocomplete
from django import forms
from django.conf import settings
from django.db import transaction
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _

from base.forms.learning_unit.edition_volume import SimplifiedVolumeManagementForm
from base.forms.learning_unit.learning_unit_create import LearningUnitModelForm, LearningContainerModelForm, \
    LearningContainerYearModelForm, LearningUnitYearModelForm
from base.forms.learning_unit.learning_unit_create_2 import LearningUnitBaseForm
from base.forms.learning_unit.learning_unit_partim import PARTIM_FORM_INHERIT_FIELDS, LearningUnitPartimModelForm, \
    merge_data
from base.forms.utils.acronym_field import ExternalAcronymField, split_acronym, ExternalPartimAcronymField
from base.models.academic_year import AcademicYear, compute_max_academic_year_adjournment
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.learning_container_year_types import EXTERNAL
from base.models.enums.learning_unit_external_sites import LearningUnitExternalSite
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.external_learning_unit_year import ExternalLearningUnitYear
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit import LearningUnit
from reference.models.country import Country
from reference.models.language import Language


class LearningContainerYearExternalModelForm(LearningContainerYearModelForm):

    def prepare_fields(self):
        self.fields["container_type"].choices = ((EXTERNAL, _("External")),)
        self.fields['container_type'].disabled = True
        self.fields['container_type'].required = False

        self.fields['type_declaration_vacant'].disabled = True
        self.fields['type_declaration_vacant'].required = False
        self.fields['is_vacant'].disabled = True
        self.fields['is_vacant'].required = False

    @staticmethod
    def clean_container_type():
        return EXTERNAL


class LearningUnitYearForExternalModelForm(LearningUnitYearModelForm):
    country_external_institution = ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        label=_("Country"),
        widget=autocomplete.ModelSelect2(
            url='country-autocomplete',
            attrs={
                'onchange': (
                    'clearAutocomplete("id_campus");'
                )
            }
        )
    )

    def __init__(self, *args, instance=None, initial=None, **kwargs):
        super().__init__(*args, instance=instance, initial=initial, external=True, **kwargs)
        self.fields['internship_subtype'].disabled = True
        if instance:
            self.fields["country_external_institution"].initial = instance.campus.organization.country and \
                                                                  instance.campus.organization.country.pk
        elif initial.get("campus"):
            self.fields["country_external_institution"].initial = initial["campus"].organization.country and\
                                                                  initial["campus"].organization.country.pk
        if not self.instance.pk:
            self.data['acronym_0'] = LearningUnitExternalSite.E.value
            self.fields['academic_year'].queryset = AcademicYear.objects.filter(
                year__gt=settings.YEAR_LIMIT_LUE_MODIFICATION,
                year__lte=compute_max_academic_year_adjournment()).order_by('year')
            self.fields['academic_year'].empty_label = None
        else:
            self.data['acronym_0'] = self.instance.acronym[0]
        self.fields['attribution_procedure'].disabled = True
        self.fields['attribution_procedure'].required = False

    class Meta(LearningUnitYearModelForm.Meta):
        fields = ('academic_year', 'acronym', 'specific_title', 'specific_title_english', 'credits',
                  'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure',
                  'professional_integration', 'campus', 'language', 'periodicity', 'other_remark', 'faculty_remark',
                  'other_remark_english')

        widgets = {
            'campus': autocomplete.ModelSelect2(
                url='campus-autocomplete',
                forward=["country_external_institution"],
                attrs={
                    'id': 'id_campus'
                }
            ),
            'credits': forms.TextInput(),
            'faculty_remark': forms.Textarea(attrs={'rows': '5'}),
            'other_remark': forms.Textarea(attrs={'rows': '5'}),
            'other_remark_english': forms.Textarea(attrs={'rows': '5'})
        }

        labels = {
            'campus': _("Reference institution")
        }


class CograduationExternalLearningUnitModelForm(forms.ModelForm):
    def __init__(self, data, person, *args, **kwargs):
        self.person = person

        super().__init__(data, *args, **kwargs)
        self.instance.author = person
        self.fields['co_graduation'].initial = True
        self.fields['co_graduation'].disabled = True
        self.fields['mobility'].initial = False
        self.fields['mobility'].disabled = True

    class Meta:
        model = ExternalLearningUnitYear
        fields = ('external_acronym', 'external_credits', 'url', 'co_graduation', 'mobility')
        widgets = {
            'external_credits': forms.TextInput(),
        }


class ExternalLearningUnitBaseForm(LearningUnitBaseForm):
    forms = OrderedDict()
    academic_year = None
    subtype = learning_unit_year_subtypes.FULL

    entity_version = None

    form_cls = form_cls_to_validate = [
        LearningUnitModelForm,
        LearningUnitYearForExternalModelForm,
        LearningContainerModelForm,
        LearningContainerYearExternalModelForm,
        SimplifiedVolumeManagementForm,
        CograduationExternalLearningUnitModelForm
    ]

    def __init__(self, person, academic_year, learning_unit_instance=None, data=None, start_year=None, proposal=False,
                 *args, **kwargs):
        self.data = data
        self.academic_year = academic_year
        self.person = person
        self.learning_unit_instance = learning_unit_instance
        self.proposal = proposal
        instances_data = self._build_instance_data(data, proposal)

        super().__init__(instances_data, *args, **kwargs)
        self.learning_unit_year_form.fields['acronym'] = ExternalAcronymField()
        if not self.instance or self.instance.acronym[0] == LearningUnitExternalSite.E.value:
            self.learning_unit_year_form.fields['acronym'].initial = LearningUnitExternalSite.E.value
            self.learning_unit_year_form.fields['acronym'].widget.widgets[0].attrs['disabled'] = True
            self.learning_unit_year_form.fields['acronym'].required = False
        self.start_year = self.instance.learning_unit.start_year if self.instance else start_year

    @property
    def learning_unit_external_form(self):
        return self.forms[CograduationExternalLearningUnitModelForm]

    @property
    def learning_container_year_form(self):
        return self.forms[LearningContainerYearExternalModelForm]

    @property
    def learning_unit_year_form(self):
        return self.forms[LearningUnitYearForExternalModelForm]

    def _build_instance_data(self, data, proposal):
        return {
            LearningUnitModelForm: {
                'data': data,
                'instance': self.instance.learning_unit if self.instance else None,
            },
            LearningContainerModelForm: {
                'data': data,
                'instance': self.instance.learning_container_year.learning_container if self.instance else None,
            },
            LearningUnitYearForExternalModelForm: self._build_instance_data_learning_unit_year(data),
            LearningContainerYearExternalModelForm: self._build_instance_data_learning_container_year(data, proposal),
            SimplifiedVolumeManagementForm: {
                'data': data,
                'proposal': proposal,
                'queryset': LearningComponentYear.objects.filter(
                    learning_unit_year=self.instance
                ) if self.instance else LearningComponentYear.objects.none(),
                'person': self.person
            },
            CograduationExternalLearningUnitModelForm: self._build_instance_data_external_learning_unit(data)
        }

    def _build_instance_data_external_learning_unit(self, data):
        return {
            'data': data,
            'instance': self.instance.externallearningunityear
            if self.instance and self.instance.is_external() else None,
            'person': self.person
        }

    def _build_instance_data_learning_unit_year(self, data):
        return {
            'data': data,
            'instance': self.instance,
            'initial': {
                'status': True,
                'academic_year': self.academic_year
            } if not self.instance else {},
            'person': self.person,
            'subtype': self.subtype
        }

    def _build_instance_data_learning_container_year(self, data, proposal):
        return {
            'data': data,
            'instance': self.instance and self.instance.learning_container_year,
            'proposal': proposal,
            'initial': {
                # Default language French
                'language': Language.objects.get(code='FR'),
            },
            'person': self.person,
            'subtype': self.subtype
        }

    def get_context(self):
        return {
            'learning_unit_year': self.instance or self.learning_unit_year_form.instance,
            'subtype': self.subtype,
            'learning_unit_form': self.learning_unit_form,
            'learning_unit_year_form': self.learning_unit_year_form,
            'learning_container_year_form': self.learning_container_year_form,
            'simplified_volume_management_form': self.simplified_volume_management_form,
            'learning_unit_external_form': self.learning_unit_external_form
        }

    @transaction.atomic()
    def save(self, commit=True):
        academic_year = self.academic_year

        learning_container = self.learning_container_form.save(commit)
        learning_unit = self.learning_unit_form.save(
            start_year=self.start_year,
            learning_container=learning_container,
            commit=commit
        )
        container_year = self.learning_container_year_form.save(
            academic_year=academic_year,
            learning_container=learning_container,
            acronym=self.learning_unit_year_form.instance.acronym,
            commit=commit
        )

        # Save learning unit year (learning_component_year)
        learning_unit_year = self.learning_unit_year_form.save(
            learning_container_year=container_year,
            learning_unit=learning_unit,
            commit=commit
        )

        self.simplified_volume_management_form.save_all_forms(
            learning_unit_year,
            commit=commit
        )

        self.learning_unit_external_form.instance.learning_unit_year = learning_unit_year
        self.learning_unit_external_form.save(commit)

        return learning_unit_year


class ExternalPartimForm(LearningUnitBaseForm):
    subtype = learning_unit_year_subtypes.PARTIM

    form_cls = [
        LearningUnitPartimModelForm,
        LearningUnitYearForExternalModelForm,
        LearningContainerModelForm,
        LearningContainerYearExternalModelForm,
        SimplifiedVolumeManagementForm,
        CograduationExternalLearningUnitModelForm,
    ]

    form_cls_to_validate = [
        LearningUnitPartimModelForm,
        LearningUnitYearForExternalModelForm,
        SimplifiedVolumeManagementForm
    ]

    def __init__(self, person, learning_unit_full_instance, academic_year, learning_unit_instance=None,
                 data=None, *args, **kwargs):
        if not isinstance(learning_unit_full_instance, LearningUnit):
            raise AttributeError('learning_unit_full arg should be an instance of {}'.format(LearningUnit))
        if learning_unit_instance is not None and not isinstance(learning_unit_instance, LearningUnit):
            raise AttributeError('learning_unit_partim_instance arg should be an instance of {}'.format(LearningUnit))
        self.person = person
        self.academic_year = academic_year
        self.learning_unit_full_instance = learning_unit_full_instance
        self.learning_unit_instance = learning_unit_instance

        self.learning_unit_year_full = self.learning_unit_full_instance.learningunityear_set.filter(
            academic_year=self.academic_year,
            subtype=FULL,
        ).get()

        # Inherit values cannot be changed by user
        inherit_luy_values = self._get_inherit_learning_unit_year_full_value()
        instances_data = self._build_instance_data(data, inherit_luy_values)

        super().__init__(instances_data, *args, **kwargs)
        self.learning_unit_year_form.fields['acronym'] = ExternalPartimAcronymField()

    @property
    def learning_unit_form(self):
        return self.forms[LearningUnitPartimModelForm]

    @property
    def learning_unit_external_form(self):
        return self.forms[CograduationExternalLearningUnitModelForm]

    @property
    def learning_container_year_form(self):
        return self.forms[LearningContainerYearExternalModelForm]

    @property
    def learning_unit_year_form(self):
        return self.forms[LearningUnitYearForExternalModelForm]

    def _build_instance_data(self, data, inherit_luy_values):
        return {
            LearningUnitPartimModelForm: self._build_instance_data_learning_unit(data),
            LearningUnitYearForExternalModelForm: self._build_instance_data_learning_unit_year(
                data,
                inherit_luy_values
            ),
            # Cannot be modify by user [No DATA args provided]
            LearningContainerModelForm: {
                'instance': self.learning_unit_year_full.learning_container_year.learning_container,
            },
            LearningContainerYearExternalModelForm: {
                'instance': self.learning_unit_year_full.learning_container_year,
                'person': self.person,
                'subtype': self.subtype
            },
            SimplifiedVolumeManagementForm: {
                'data': data,
                'queryset': LearningComponentYear.objects.filter(
                    learning_unit_year=self.instance)
                if self.instance else LearningComponentYear.objects.none(),
                'person': self.person,
            },
            CograduationExternalLearningUnitModelForm: self._build_instance_data_external_learning_unit(data)
        }

    def _build_instance_data_external_learning_unit(self, data):
        return {
            'data': data,
            'instance': self.instance.externallearningunityear
            if self.instance and self.instance.is_external() else None,
            'person': self.person
        }

    def _build_instance_data_learning_unit_year(self, data, inherit_luy_values):
        return {
            'data': merge_data(data, inherit_luy_values),
            'instance': self.instance,
            'initial': self._get_initial_learning_unit_year_form() if not self.instance else None,
            'person': self.person,
            'subtype': self.subtype
        }

    def _build_instance_data_learning_unit(self, data):
        return {
            'data': data,
            'instance': self.instance.learning_unit if self.instance else None,
            'start_year': self.learning_unit_year_full.academic_year,
            'max_end_year': self.learning_unit_year_full.learning_unit.max_end_year
        }

    def _get_inherit_learning_unit_year_full_value(self):
        """This function will return the inherit value come from learning unit year FULL"""
        return {field: value for field, value in self._get_initial_learning_unit_year_form().items()
                if field in PARTIM_FORM_INHERIT_FIELDS}

    def _get_initial_learning_unit_year_form(self):
        acronym = self.instance.acronym if self.instance else self.learning_unit_year_full.acronym
        initial_learning_unit_year = {
            'acronym': acronym,
            'academic_year': self.learning_unit_year_full.academic_year.id,
            'internship_subtype': self.learning_unit_year_full.internship_subtype,
            'attribution_procedure': self.learning_unit_year_full.attribution_procedure,
            'subtype': self.subtype,
            'credits': self.learning_unit_year_full.credits,
            'session': self.learning_unit_year_full.session,
            'quadrimester': self.learning_unit_year_full.quadrimester,
            'status': self.learning_unit_year_full.status,
            'specific_title': self.learning_unit_year_full.specific_title,
            'specific_title_english': self.learning_unit_year_full.specific_title_english,
            'language': self.learning_unit_year_full.language,
            'campus': self.learning_unit_year_full.campus,
            'periodicity': self.learning_unit_year_full.periodicity
        }
        acronym_splited = split_acronym(acronym, instance=self.instance)
        initial_learning_unit_year.update({
            "acronym_{}".format(idx): acronym_part for idx, acronym_part in enumerate(acronym_splited)
        })
        return initial_learning_unit_year

    def save(self, commit=True):
        start_year = self.instance.learning_unit.start_year if self.instance else \
            self.learning_unit_full_instance.start_year

        lcy = self.learning_unit_year_full.learning_container_year
        # Save learning unit
        learning_unit = self.learning_unit_form.save(
            start_year=start_year,
            learning_container=lcy.learning_container,
            commit=commit
        )

        # Save learning unit year
        learning_unit_yr = self.learning_unit_year_form.save(
            learning_container_year=lcy,
            learning_unit=learning_unit,
            commit=commit
        )

        self.simplified_volume_management_form.save_all_forms(
            learning_unit_yr,
            commit=commit
        )

        self.learning_unit_external_form.instance.learning_unit_year = learning_unit_yr
        self.learning_unit_external_form.save(commit)

        return learning_unit_yr

    def get_context(self):
        return {
            'learning_unit_year': self.instance,
            'subtype': self.subtype,
            'learning_unit_form': self.learning_unit_form,
            'learning_unit_year_form': self.learning_unit_year_form,
            'learning_container_year_form': self.learning_container_year_form,
            'simplified_volume_management_form': self.simplified_volume_management_form,
            'learning_unit_external_form': self.learning_unit_external_form
        }
