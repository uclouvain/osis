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

from base import models as mdl
from base.forms.common import STEP_HALF_INTEGER
from base.models.learning_component_year import LearningComponentYear


class LearningUnitComponentEditForm(forms.ModelForm):
    used_by = forms.BooleanField(required=False)

    class Meta:
        model = LearningComponentYear
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'hourly_volume_total_annual': forms.TextInput(),
            'hourly_volume_partial_q1': forms.TextInput(),
            'hourly_volume_partial_q2': forms.TextInput(),
            'volume_declared_vacant': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year', None)
        super(LearningUnitComponentEditForm, self).__init__(*args, **kwargs)

    def load_initial(self):
        self.fields['used_by'].initial = _get_links_between_learning_unit_and_component(self.learning_unit_year,
                                                                                        self.instance).exists()

    def save(self, commit=True):
        super(LearningUnitComponentEditForm, self).save(commit)
        used_by = self.cleaned_data.get('used_by')
        if used_by:
            _create_link(self.learning_unit_year, self.instance)
        else:
            _delete_link(self.learning_unit_year, self.instance)


def _get_links_between_learning_unit_and_component(learning_unit_year, learning_component_year):
    return mdl.learning_unit_component.search(learning_component_year, learning_unit_year)


def _create_link(learning_unit_year, learning_component_year):
    # Create a link between learning_unit_year and learning_component_year
    links = _get_links_between_learning_unit_and_component(learning_unit_year, learning_component_year)
    if not links.exists():
        new_learning_unit_component = mdl.learning_unit_component.LearningUnitComponent(
            learning_unit_year=learning_unit_year,
            learning_component_year=learning_component_year)
        new_learning_unit_component.save()


def _delete_link(learning_unit_year, learning_component_year):
    # If exists delete link between learning_unit_year and learning_component_year
    links = _get_links_between_learning_unit_and_component(learning_unit_year, learning_component_year)
    if links.exists():
        for l in links:
            l.delete()
