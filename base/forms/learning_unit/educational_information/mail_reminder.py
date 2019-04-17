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

from base.forms.utils.emptyfield import EmptyField


class MailReminderRow(forms.Form):
    responsible = EmptyField(label='')
    learning_unit_years = EmptyField(label='')
    check = forms.BooleanField(required=False, label='')
    person_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.person = kwargs.pop('person', None)
        self.learning_unit_years = kwargs.pop('learning_unit_years', [])
        super().__init__(*args, **kwargs)

        self.initial['check'] = True
        self.initial['responsible'] = self.person
        if self.person:
            self.initial['person_id'] = self.person.id
            self.fields["responsible"].label = "{}  {}".format(self.person.last_name, self.person.first_name)

        acronym_list = _get_acronyms_concatenation(self.learning_unit_years)
        self.initial['learning_unit_years'] = acronym_list
        self.fields["learning_unit_years"].label = acronym_list
        self.fields["responsible"].widget.attrs['class'] = 'no_label'


def _get_acronyms_concatenation(learning_unit_years):
    return ', '.join([learning_unit_yr.acronym for learning_unit_yr in learning_unit_years])


class MailReminderFormset(forms.BaseFormSet):

    def __init__(self, *args, list_responsible=None,  **kwargs):
        self.list_responsible = list_responsible
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        if self.list_responsible:
            kwargs['person'] = self.list_responsible[index].get('person')
            kwargs['learning_unit_years'] = self.list_responsible[index].get('learning_unit_years')
        return kwargs

    def get_checked_responsibles(self):
        return [{'person': form.cleaned_data.get('person_id'),
                 'learning_unit_years': form.cleaned_data.get('learning_unit_years')} for form in self.forms if
                form.cleaned_data.get('check')]
