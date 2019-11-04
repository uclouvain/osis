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
from ckeditor.widgets import CKEditorWidget
from django import forms

from base.forms.common import set_trans_txt
from cms.enums import entity_name
from cms.models import translated_text


class LearningUnitSpecificationsForm(forms.Form):
    learning_unit_year = language = None

    def __init__(self, learning_unit_year, language, *args, **kwargs):
        self.learning_unit_year = learning_unit_year
        self.language = language
        self.refresh_data()
        super(LearningUnitSpecificationsForm, self).__init__(*args, **kwargs)

    def refresh_data(self):
        language_iso = self.language[0]
        texts_list = translated_text.search(entity=entity_name.LEARNING_UNIT_YEAR,
                                            reference=self.learning_unit_year.id,
                                            language=language_iso) \
            .exclude(text__isnull=True)

        set_trans_txt(self, texts_list)


class LearningUnitSpecificationsEditForm(forms.Form):
    trans_text_fr = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    trans_text_en = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    cms_fr_id = forms.IntegerField(widget=forms.HiddenInput, required=True)
    cms_en_id = forms.IntegerField(widget=forms.HiddenInput, required=True)

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year', None)
        self.text_label = kwargs.pop('text_label', None)
        super(LearningUnitSpecificationsEditForm, self).__init__(*args, **kwargs)

    def load_initial(self):
        value_fr = translated_text.get_or_create(
            entity=entity_name.LEARNING_UNIT_YEAR,
            reference=self.learning_unit_year.id,
            language='fr-be',
            text_label=self.text_label
        )
        value_en = translated_text.get_or_create(
            entity=entity_name.LEARNING_UNIT_YEAR,
            reference=self.learning_unit_year.id,
            language='en',
            text_label=self.text_label
        )
        self.fields['cms_fr_id'].initial = value_fr.id
        self.fields['trans_text_fr'].initial = value_fr.text
        self.fields['cms_en_id'].initial = value_en.id
        self.fields['trans_text_en'].initial = value_en.text

    def save(self):
        self._save_text_language('fr')
        self._save_text_language('en')

    def _save_text_language(self, language):
        trans_text = translated_text.find_by_id(self.cleaned_data['cms_' + language + '_id'])
        trans_text.text = self.cleaned_data.get('trans_text_' + language)
        trans_text.save()
