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
from django.utils.translation import gettext_lazy as _

from base.forms.common import ValidationRuleMixin
from base.forms.education_group.common import MainCampusChoiceField, MainEntitiesVersionChoiceField
from base.models.academic_year import AcademicYear
from base.models.enums.constraint_type import ConstraintTypeEnum


class GroupForm(ValidationRuleMixin, forms.Form):
    code = forms.CharField(max_length=15, label=_("Code"), required=False)
    academic_year = forms.ModelChoiceField(queryset=AcademicYear.objects.all(), label=_("Validity"), required=False)
    abbreviated_title = forms.CharField(max_length=40, label=_("Acronym/Short title"), required=False)
    title_fr = forms.CharField(max_length=240, label=_("Title in French"), required=False)
    title_en = forms.CharField(max_length=240, label=_("Title in English"), required=False)
    credits = forms.CharField(label=_("Credits"), required=False)
    constraint_type = forms.ChoiceField(
        choices=ConstraintTypeEnum.choices(),
        label=_("Type of constraint"),
        required=False
    )
    min_constraint = forms.CharField(label=_("minimum constraint"), required=False)
    max_constraint = forms.CharField(label=_("maximum constraint"), required=False)
    management_entity = MainEntitiesVersionChoiceField(queryset=None, label=_("Management entity"), required=False)
    teaching_campus = MainCampusChoiceField(queryset=None, label=_("Learning location"), required=False)
    remark_fr = forms.CharField(widget=forms.Textarea, label=_("Remark"), required=False)
    remark_en = forms.CharField(widget=forms.Textarea, label=_("remark in english"), required=False)

    def __init__(self, *args, user, group_type, **kwargs):
        self.user = user
        self.group_type = group_type
        super().__init__(*args, **kwargs)

    # ValidationRuleMixin
    def field_reference(self, field_name: str):
        return '.'.join(["GroupForm", self.group_type, field_name])

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

    def clean_management_entity(self):
        if self.cleaned_data['management_entity']:
            return self.cleaned_data['management_entity'].most_recent_acronym
        return None
