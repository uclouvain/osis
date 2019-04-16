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

from base import models as mdl


class LearningClassEditForm(forms.ModelForm):
    used_by = forms.BooleanField(required=False)

    class Meta:
        model = mdl.learning_class_year.LearningClassYear
        fields = ['description', ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
        }

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year', None)
        self.learning_component_year = kwargs.pop('learning_component_year', None)
        super(LearningClassEditForm, self).__init__(*args, **kwargs)

    def load_initial(self):
        self.fields['used_by'].initial = _get_links_between_learning_unit_component_and_class(
            self.learning_unit_year,
            self.learning_component_year,
            self.instance).exists()

    def save(self, commit=True):
        super(LearningClassEditForm, self).save(commit)
        used_by = self.cleaned_data.get('used_by')
        if used_by:
            self.create_link()
        else:
            self.delete_link()

    def link_management(self, used_by):
        if used_by:
            self.create_link()
        else:
            self.delete_link()

    def create_link(self):
        # Create a link between learning_class_year and learning_unit_component
        links = _get_links_between_learning_unit_component_and_class(
            self.learning_unit_year,
            self.learning_component_year,
            self.instance
        )
        if not links.exists():
            learning_unit_component = mdl.learning_unit_component.search(self.learning_component_year,
                                                                         self.learning_unit_year).first()
            new_learning_unit_component_class = mdl.learning_unit_component_class.LearningUnitComponentClass(
                learning_class_year=self.instance,
                learning_unit_component=learning_unit_component)
            new_learning_unit_component_class.save()

    def delete_link(self):
        links = _get_links_between_learning_unit_component_and_class(
            self.learning_unit_year,
            self.learning_component_year,
            self.instance
        )
        if links.exists():
            for l in links:
                l.delete()


def _get_links_between_learning_unit_component_and_class(learning_unit_year,
                                                         learning_component_year,
                                                         learning_class_year):
    learning_unit_component_ids = list(mdl.learning_unit_component.search(learning_component_year, learning_unit_year)
                                       .values_list('id', flat=True))
    return mdl.learning_unit_component_class.search(
        learning_unit_component=learning_unit_component_ids,
        learning_class_year=learning_class_year
    )
