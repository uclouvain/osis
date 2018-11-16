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
from django import forms
from django.utils.translation import ugettext_lazy as _

from base.models.prerequisite import Prerequisite, prerequisite_syntax_validator


class LearningUnitPrerequisiteForm(forms.ModelForm):
    prerequisite_string = forms.CharField(
        label=_("Prerequisite"),
        validators=[prerequisite_syntax_validator],
        help_text=_("prerequisites_syntax_rules"),
    )

    class Meta:
        model = Prerequisite
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prerequisite_string'].initial = self.instance.prerequisite_string

    def save(self, commit=True):
        print(self.cleaned_data['prerequisite_string'])
        return super(LearningUnitPrerequisiteForm, self).save(commit=commit)
