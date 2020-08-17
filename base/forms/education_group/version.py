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
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _

from base.forms.utils.choice_field import BLANK_CHOICE
from base.models import academic_year
from base.models.academic_year import compute_max_academic_year_adjournment
from education_group.ddd.business_types import *


class SpecificVersionForm(forms.Form):
    version_name = forms.CharField(
        max_length=15,
        required=True,
        label=_('Acronym of version'),
        widget=TextInput(
            attrs={'onchange': 'validate_version_name()'}
        ),
    )
    title = forms.CharField(
        max_length=100,
        required=False,
        label=_('Full title of the french version'),
    )
    title_english = forms.CharField(
        max_length=100,
        required=False,
        label=_('Full title of the english version'),
    )
    end_year = forms.ChoiceField(
        required=False,
        label=_('This version exists until'),
    )

    def __init__(self, training_identity: 'TrainingIdentity', *args, **kwargs):
        self.training_identity = training_identity
        super().__init__(*args, **kwargs)

        self.__init_academic_year_choices()

    def __init_academic_year_choices(self):
        max_year = academic_year.find_academic_year_by_year(compute_max_academic_year_adjournment() + 1).year
        choices_years = [(x, x) for x in range(self.training_identity.year, max_year)]
        self.fields["end_year"].choices = BLANK_CHOICE + choices_years

    def clean_end_year(self):
        end_year = self.cleaned_data["end_year"]
        return int(end_year) if end_year else None
