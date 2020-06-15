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

from base.forms.education_group.common import MainCampusChoiceField, MainEntitiesVersionChoiceField
from base.models.academic_year import AcademicYear


class GroupForm(forms.Form):
    code = forms.CharField(max_length=15, label=_("Code"))
    academic_year = forms.ModelChoiceField(queryset=AcademicYear.objects.all(), label=_("Validity"))
    abbreviated_title = forms.CharField(max_length=40, label=_("Acronym/Short title"))
    title_fr = forms.CharField(max_length=240, label=_("Title in French"))
    title_en = forms.CharField(max_length=240, label=_("Title in English"))
    credits = forms.CharField(label=_("Credits"))
    constraint_type = forms.ChoiceField(label=_("Type of constraint"))
    min_constraint = forms.CharField(label=_("minimum constraint"))
    max_constraint = forms.CharField(label=_("maximum constraint"))
    management_entity = MainEntitiesVersionChoiceField(queryset=None, label=_("Management entity"))
    teaching_campus = MainCampusChoiceField(queryset=None, label=_("Learning location"))
    remark_fr = forms.CharField(widget=forms.Textarea, label=_("Remark"))
    remark_en = forms.CharField(widget=forms.Textarea, label=_("remark in english"))

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
