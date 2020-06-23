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
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from base.models.education_group_type import EducationGroupType
from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import MiniTrainingType, GroupType
from program_management.business.group_element_years import management

DISABLED_OFFER_TYPE = [
    MiniTrainingType.FSA_SPECIALITY.name,
    MiniTrainingType.MOBILITY_PARTNERSHIP.name,
    GroupType.MAJOR_LIST_CHOICE.name,
    GroupType.MOBILITY_PARTNERSHIP_LIST_CHOICE.name
]


class EducationGroupTypeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_name_display()


class SelectTypeForm(forms.Form):
    name = EducationGroupTypeModelChoiceField(
        EducationGroupType.objects.none(),
        label=_("Type of training"),
        required=True,
    )

    def __init__(self, category, parent=None, *args, **kwargs):
        self.parent = parent

        super().__init__(*args, **kwargs)
        self.fields["name"].label = _("Which type of %(category)s do you want to create ?") % {
            "category": Categories[category].value
        }
        self.fields["name"].queryset = EducationGroupType.objects.filter(category=category)

    def clean_name(self):
        education_group_type = self.cleaned_data["name"]

        # TODO: Use ValidateAuthorizedRelationshipForAllTrees instead
        if self.parent and management.is_max_child_reached(self.parent, education_group_type.name):
            raise ValidationError(
                _("The number of children of type \"%(child_type)s\" for \"%(parent)s\" "
                  "has already reached the limit.") % {
                    'child_type': education_group_type.get_name_display(),
                    'parent': self.parent
                })
        return education_group_type.name
