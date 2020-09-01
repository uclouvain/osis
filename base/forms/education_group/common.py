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
from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied, ImproperlyConfigured, ValidationError
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from base.business.education_groups import create
from base.business.event_perms import EventPermEducationGroupEdition
from base.forms.common import ValidationRuleMixin
from base.models import campus, group_element_year
from base.models.academic_year import current_academic_year
from base.models.campus import Campus
from base.models.education_group import EducationGroup
from base.models.education_group_type import find_authorized_types
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import get_last_version, EntityVersion
from base.models.enums import education_group_categories, groups
from base.models.enums.education_group_categories import TRAINING
from base.models.enums.education_group_types import MiniTrainingType, GroupType
from education_group.models.group_year import GroupYear
from osis_role.contrib.forms.fields import EntityRoleChoiceField
from reference.models.language import Language
from rules_management.enums import TRAINING_PGRM_ENCODING_PERIOD, TRAINING_DAILY_MANAGEMENT, \
    MINI_TRAINING_PGRM_ENCODING_PERIOD, MINI_TRAINING_DAILY_MANAGEMENT, GROUP_PGRM_ENCODING_PERIOD, \
    GROUP_DAILY_MANAGEMENT
from rules_management.mixins import PermissionFieldMixin

DISABLED_OFFER_TYPE = [
    MiniTrainingType.FSA_SPECIALITY.name,
    MiniTrainingType.MOBILITY_PARTNERSHIP.name,
    GroupType.MAJOR_LIST_CHOICE.name,
    GroupType.MOBILITY_PARTNERSHIP_LIST_CHOICE.name
]


class MainCampusChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset, *args, **kwargs):
        queryset = campus.find_main_campuses()
        super().__init__(queryset, *args, **kwargs)


class ManagementEntitiesVersionChoiceField(EntityRoleChoiceField):
    def __init__(self, person, initial, **kwargs):
        group_names = (groups.FACULTY_MANAGER_GROUP, groups.CENTRAL_MANAGER_GROUP, )
        self.initial = initial
        super().__init__(
            person=person,
            group_names=group_names,
            label=_('Management entity'),
            **kwargs,
        )

    def get_queryset(self):
        qs = super().get_queryset().pedagogical_entities().order_by('acronym')
        if self.initial:
            qs |= EntityVersion.objects.filter(pk=self.initial)
        return qs


class EducationGroupTypeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_name_display()


class ValidationRuleEducationGroupTypeMixin(ValidationRuleMixin):
    """
    ValidationRuleMixin For EducationGroupType

    The object reference must be structured like that:
        {db_table_name}.{col_name}.{education_group_type_name}
    """

    def field_reference(self, name):
        return super().field_reference(name) + '.' + self.get_type()

    def get_type(self):
        # For creation
        if self.education_group_type:
            return self.education_group_type.external_id
        # For updating
        elif self.instance and self.instance.education_group_type:
            return self.instance.education_group_type.external_id
        return ""


class PermissionFieldEducationGroupMixin(PermissionFieldMixin):
    """
    Permission Field for educationgroup

    This mixin will get allowed field on reference_field model according to perms
    """

    def is_edition_period_opened(self):
        return EventPermEducationGroupEdition().is_open()

    def get_context(self):
        is_open = self.is_edition_period_opened()
        if self.category == education_group_categories.TRAINING:
            return TRAINING_PGRM_ENCODING_PERIOD if is_open else TRAINING_DAILY_MANAGEMENT
        elif self.category == education_group_categories.MINI_TRAINING:
            return MINI_TRAINING_PGRM_ENCODING_PERIOD if is_open else MINI_TRAINING_DAILY_MANAGEMENT
        elif self.category == education_group_categories.GROUP:
            return GROUP_PGRM_ENCODING_PERIOD if is_open else GROUP_DAILY_MANAGEMENT
        return super().get_context()


class PermissionFieldEducationGroupYearMixin(PermissionFieldEducationGroupMixin):
    """
    Permission Field for educationgroupyear

    This mixin will get allowed field on reference_field model according to perms and egy related period
    """

    def is_edition_period_opened(self):
        education_group_year = self.instance if hasattr(self.instance, 'academic_year') else None
        dummy_group_year = GroupYear(academic_year=education_group_year.academic_year) if education_group_year else None
        return EventPermEducationGroupEdition(obj=dummy_group_year, raise_exception=False).is_open()


class PermissionFieldTrainingMixin(PermissionFieldEducationGroupYearMixin):
    """
    Permission Field for Hops(year) and for Coorganization

    This mixin will get allowed field on reference_field model according to perm's
    """

    def __init__(self, *args, **kwargs):
        self.category = TRAINING
        super().__init__(*args, **kwargs)


# TODO: Only used in program_management/ ==> Move to it ?
class SelectLanguage(forms.Form):
    language = forms.ChoiceField(widget=forms.RadioSelect,
                                 choices=settings.LANGUAGES,
                                 label=_('Select a language'),
                                 required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['language'] = translation.get_language()
