##############################################################################
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
##############################################################################
from typing import Dict

from ajax_select.fields import AutoCompleteSelectMultipleField
from dal import autocomplete
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from base.business.event_perms import EventPermEducationGroupEdition
from base.forms.common import ValidationRuleMixin
from base.forms.education_group.common import MainCampusChoiceField, MainEntitiesVersionChoiceField
from base.forms.education_group.training import _get_section_choices
from base.forms.utils.choice_field import BLANK_CHOICE
from base.models.academic_year import AcademicYear
from base.models.campus import Campus
from base.models.enums.academic_type import AcademicTypes
from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.activity_presence import ActivityPresence
from base.models.enums.constraint_type import ConstraintTypeEnum
from base.models.enums.decree_category import DecreeCategories
from base.models.enums.duration_unit import DurationUnits
from base.models.enums.education_group_types import TrainingType
from base.models.enums.funding_codes import FundingCodes
from base.models.enums.internship_presence import InternshipPresence
from base.models.enums.rate_code import RateCode
from base.models.enums.schedule_type import ScheduleTypeEnum
from education_group.forms import fields
from reference.models.domain import Domain
from reference.models.domain_isced import DomainIsced
from reference.models.enums.domain_type import UNIVERSITY
from reference.models.language import Language
from rules_management.enums import GROUP_PGRM_ENCODING_PERIOD, GROUP_DAILY_MANAGEMENT, TRAINING_PGRM_ENCODING_PERIOD, \
    TRAINING_DAILY_MANAGEMENT
from rules_management.mixins import PermissionFieldMixin


class CreateTrainingForm(ValidationRuleMixin, PermissionFieldMixin, forms.Form):

    # panel_informations_form.html
    acronym = forms.CharField(max_length=15, label=_("Acronym/Short title"), required=False)
    active = forms.ChoiceField(
        initial=ActiveStatusEnum.ACTIVE,
        choices=BLANK_CHOICE + list(ActiveStatusEnum.choices()),
        label=_("Status"),
    )
    schedule_type = forms.ChoiceField(
        initial=ScheduleTypeEnum.DAILY,
        choices=BLANK_CHOICE + list(ScheduleTypeEnum.choices()),
        label=_("Schedule type"),
    )
    credits = forms.IntegerField(
        label=_("Credits"),
        required=False,
        widget=forms.TextInput(),
    )
    title = forms.CharField(max_length=240, label=_("Title in French"))
    title_english = forms.CharField(max_length=240, label=_("Title in English"), required=False)
    partial_title = forms.CharField(max_length=240, label=_("Partial title in French"), required=False)
    partial_title_english = forms.CharField(max_length=240, label=_("Partial title in English"), required=False)
    keywords = forms.CharField(max_length=320, label=_('Keywords'))

    # panel_academic_informations_form.html
    academic_type = forms.ChoiceField(
        choices=BLANK_CHOICE + list(AcademicTypes.choices()),
        label=_("Academic type"),
        required=False,
    )
    duration = forms.IntegerField(
        initial=1,
        label=_("Duration"),
        required=False,
        validators=[MinValueValidator(1)],
        widget=forms.TextInput(),
    )
    duration_unit = forms.ChoiceField(
        initial=DurationUnits.QUADRIMESTER.value,
        choices=BLANK_CHOICE + list(DurationUnits.choices()),
        label=_("duration unit"),
        required=False,
    )
    internship = forms.ChoiceField(
        initial=InternshipPresence.NO.value,
        choices=BLANK_CHOICE + list(InternshipPresence.choices()),
        label=_("Internship"),
        required=False,
    )
    enrollment_enabled = forms.BooleanField(initial=False, label=_('Enrollment enabled'))
    has_online_re_registration = forms.BooleanField(initial=True, label=_('Web re-registration'))
    has_partial_deliberation = forms.BooleanField(initial=False, label=_('Partial deliberation'))
    has_admission_exam = forms.BooleanField(initial=False, label=_('Admission exam'))
    has_dissertation = forms.BooleanField(initial=False, label=_('dissertation'))
    produce_university_certificate = forms.BooleanField(initial=False, label=_('University certificate'))
    decree_category = forms.ChoiceField(
        choices=BLANK_CHOICE + list(DecreeCategories.choices()).sort(key=lambda c: c[1]),
        label=_("Decree category"),
        required=False,
    )
    rate_code = forms.ChoiceField(
        choices=BLANK_CHOICE + list(RateCode.choices()).sort(key=lambda c: c[1]),
        label=_("Rate code"),
        required=False,
    )
    main_language = forms.ModelChoiceField(  # FIXME :: to replace by choice field (to prevent link to DB model)
        queryset=Language.objects.all().order_by('name'),
        required=False,
        label=_('Primary language'),
    )
    english_activities = forms.ChoiceField(
        choices=BLANK_CHOICE + list(ActivityPresence.choices()),
        label=_("activities in English"),
        required=False,
    )
    other_language_activities = forms.ChoiceField(
        choices=BLANK_CHOICE + list(ActivityPresence.choices()),
        label=_("Other languages activities"),
        required=False,
    )
    main_domain = forms.ModelChoiceField(
        queryset=Domain.objects.filter(type=UNIVERSITY).select_related('decree')
    )
    secondary_domains = AutoCompleteSelectMultipleField(
        'university_domains',
        required=False,
        help_text=_('Enter text to search'),
        show_help_text=True,
        label=_('secondary domains').title(),
    )
    isced_domain = forms.ModelChoiceField(queryset=DomainIsced.objects.all())
    internal_comment = forms.CharField(max_length=500, label=_("comment (internal)"), required=False)

    # panel_entities_form.html
    management_entity = fields.ManagementEntitiesChoiceField(person=None, initial=None, required=False)
    administration_entity = MainEntitiesVersionChoiceField(queryset=None)  # FIXME :: class to move into 'fields.py'
    academic_year = forms.ModelChoiceField(
        queryset=EventPermEducationGroupEdition.get_academic_years().filter(
            year__gte=settings.YEAR_LIMIT_EDG_MODIFICATION
        ),
        label=_("Start"),
    )  # Equivalent to start_year
    end_year = forms.ModelChoiceField(
        queryset=EventPermEducationGroupEdition.get_academic_years().filter(
            year__gte=settings.YEAR_LIMIT_EDG_MODIFICATION
        ),
        label=_('Last year of organization'),
    )
    teaching_campus = MainCampusChoiceField(queryset=None, label=_("Learning location"), required=False)
    enrollment_campus = forms.ModelChoiceField(  # FIXME :: to replace by choice field (to prevent link to DB model)
        queryset=Campus.objects.all(),
        label=_("Enrollment campus"),
        required=False,
    )
    other_campus_activities = forms.ChoiceField(
        choices=BLANK_CHOICE + list(ActivityPresence.choices()),
        label=_("Activities on other campus"),
        required=False,
    )

    # panel_funding_form.html
    can_be_funded = forms.BooleanField(initial=False, label=_('Funding'))
    funding_direction = forms.ChoiceField(
        choices=BLANK_CHOICE + list(FundingCodes.choices()),
        label=_("Funding direction"),
        required=False,
    )
    can_be_international_funded = forms.BooleanField(initial=False, label=_('Funding international cooperation CCD/CUD'))
    international_funding_orientation = forms.ChoiceField(
        choices=BLANK_CHOICE + list(FundingCodes.choices()),
        label=_("Funding international cooperation CCD/CUD direction"),
        required=False,
    )

    # panel_remarks_form.html  # FIXME :: group form ??
    remark_fr = forms.CharField(widget=forms.Textarea, label=_("Remark"), required=False)
    remark_english = forms.CharField(widget=forms.Textarea, label=_("remark in english"), required=False)

    # HOPS panel
    hops_fields = ('ares_study', 'ares_graca', 'ares_ability')
    ares_study = forms.CharField(widget=forms.TextInput(), required=False)
    ares_graca = forms.CharField(widget=forms.TextInput(), required=False)
    ares_ability = forms.CharField(widget=forms.TextInput(), required=False)
    code_inter_cfb = forms.CharField(max_length=8, label=_('Code co-graduation inter CfB'), required=False)
    coefficient = forms.DecimalField(widget=forms.TextInput())

    # FIXME :: reuse groupForm instead ?
    # academic_year = forms.ModelChoiceField(queryset=AcademicYear.objects.all(), label=_("Validity"), required=False)
    # code = forms.CharField(max_length=15, label=_("Code"), required=False)
    # constraint_type = forms.ChoiceField(
    #     choices=BLANK_CHOICE + list(ConstraintTypeEnum.choices()),
    #     label=_("Type of constraint"),
    #     required=False,
    # )
    # min_constraint = forms.IntegerField(
    #     label=_("minimum constraint"),
    #     required=False,
    #     widget=forms.TextInput
    # )
    # max_constraint = forms.IntegerField(
    #     label=_("maximum constraint"),
    #     required=False,
    #     widget=forms.TextInput
    # )

    # Diploma tab
    section = forms.ChoiceField(choices=lazy(_get_section_choices, list), required=False)
    joint_diploma = forms.BooleanField(initial=False, label=_('Leads to diploma/certificate'))
    diploma_printing_title = forms.CharField(max_length=240, required=False, label=_('Diploma title'))
    professional_title = forms.CharField(max_length=320, required=False, label=_('Professionnal title'))
    certificate_aims = autocomplete.ModelSelect2Multiple(
        url='certificate_aim_autocomplete',
        attrs={
            'data-html': True,
            'data-placeholder': _('Search...'),
            'data-width': '100%',
        },
        forward=['section'],
    ),

    def __init__(self, *args, user: User, training_type: str, **kwargs):
        self.user = user
        self.training_type = training_type

        super().__init__(*args, **kwargs)

        self.__init_academic_year_field()
        self.__init_management_entity_field()
        self.__init_certificate_aims_field()
        self.__init_diploma_fields()

    def __init_academic_year_field(self):
        if not self.fields['academic_year'].disabled and self.user.person.is_faculty_manager:
            self.fields['academic_year'].queryset = EventPermEducationGroupEdition.get_academic_years() \
                .filter(year__gte=settings.YEAR_LIMIT_EDG_MODIFICATION)
        else:
            self.fields['academic_year'].queryset = self.fields['academic_year'].queryset.filter(
                year__gte=settings.YEAR_LIMIT_EDG_MODIFICATION
            )

            self.fields['academic_year'].label = _('Start')

    def __init_management_entity_field(self):
        self.fields['management_entity'] = fields.ManagementEntitiesChoiceField(
            person=self.user.person,
            initial=None,
            disabled=self.fields['management_entity'].disabled,
        )

    def __init_certificate_aims_field(self):
        if not self.fields['certificate_aims'].disabled:
            self.fields['section'].disabled = False

    def __init_diploma_fields(self):
        if self.training_type in TrainingType.with_diploma_values_set_initially_as_true():
            self.fields['joint_diploma'].initial = True
            self.fields['diploma_printing_title'].required = True
        else:
            self.fields['joint_diploma'].initial = False
            self.fields['diploma_printing_title'].required = False

    def is_valid(self):
        valid = super(CreateTrainingForm, self).is_valid()

        hops_fields_values = [self.cleaned_data.get(hops_field) for hops_field in self.hops_fields]
        if any(hops_fields_values) and not all(hops_fields_values):
            self.add_error(
                self.hops_fields[0],
                _('The fields concerning ARES have to be ALL filled-in or none of them')
            )
            valid = False

        return valid

    # ValidationRuleMixin
    def field_reference(self, field_name: str) -> str:
        return '.'.join(["TrainingForm", self.training_type, field_name])

    # PermissionFieldMixin
    def get_context(self) -> str:
        is_edition_period_opened = EventPermEducationGroupEdition(raise_exception=False).is_open()
        return TRAINING_PGRM_ENCODING_PERIOD if is_edition_period_opened else TRAINING_DAILY_MANAGEMENT

    # PermissionFieldMixin
    def get_model_permission_filter_kwargs(self) -> Dict:
        return {'context': self.get_context()}

    def clean_academic_year(self):
        if self.cleaned_data['academic_year']:
            return self.cleaned_data['academic_year'].year
        return None

    def clean_teaching_campus(self):
        if self.cleaned_data['teaching_campus']:
            return {
                'name': self.cleaned_data['teaching_campus'].name,
                'organization_name': self.cleaned_data['teaching_campus'].organization.name,
            }
        return None

    def clean_code(self):
        data_cleaned = self.cleaned_data['code']
        if data_cleaned:
            return data_cleaned.upper()

    def clean_abbreviated_title(self):
        data_cleaned = self.cleaned_data['abbreviated_title']
        if data_cleaned:
            return data_cleaned.upper()


class UpdateTrainingForm(CreateTrainingForm):

    def __init__(self, *args, **kwargs):
        super(UpdateTrainingForm, self).__init__(*args, **kwargs)
        self.fields['academic_year'].label = _('Validity')
