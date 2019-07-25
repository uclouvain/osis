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
from django.utils.translation import gettext_lazy as _

from base.models.learning_achievement import LearningAchievement
from reference.models import language
from reference.models.language import EN_CODE_LANGUAGE, FR_CODE_LANGUAGE


class LearningAchievementEditForm(forms.ModelForm):
    text_fr = forms.CharField(
        widget=CKEditorWidget(config_name='minimal_plus_headers'),
        required=False,
        label=_('French')
    )
    text_en = forms.CharField(
        widget=CKEditorWidget(config_name='minimal_plus_headers'),
        required=False,
        label=_('English')
    )
    lua_fr_id = forms.IntegerField(widget=forms.HiddenInput)
    lua_en_id = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = LearningAchievement
        fields = ['code_name', 'text_fr', 'text_en']

    def __init__(self, data=None, initial=None, **kwargs):
        initial = initial or {}

        self.luy = kwargs.pop('luy', None)
        self.code = kwargs.pop('code', None)

        if data and data.get('language_code'):
            initial['language'] = language.find_by_code(data.get('language_code'))

        super().__init__(data, initial=initial, **kwargs)

        self._get_code_name_disabled_status()

        for key, value in initial.items():
            setattr(self.instance, key, value)

    def load_initial(self):
        value_fr, _ = LearningAchievement.objects.get_or_create(
            learning_unit_year_id=self.luy.id,
            code_name=self.code if self.code else '',
            language=language.find_by_code(FR_CODE_LANGUAGE)
        )
        value_en, _ = LearningAchievement.objects.get_or_create(
            learning_unit_year_id=self.luy.id,
            code_name=self.code if self.code else '',
            language=language.find_by_code(EN_CODE_LANGUAGE)
        )
        self.fields['text_fr'].initial = value_fr.text
        self.fields['text_en'].initial = value_en.text
        self.fields['lua_fr_id'].initial = value_fr.id
        self.fields['lua_en_id'].initial = value_en.id
        self.fields['code_name'].initial = value_fr.code_name

    def _get_code_name_disabled_status(self):
        if self.instance.pk and self.instance.language.code == EN_CODE_LANGUAGE:
            self.fields["code_name"].disabled = True

    def save(self, commit=True):
        text_fr = LearningAchievement.objects.get(id=self.cleaned_data['lua_fr_id'])
        text_en = LearningAchievement.objects.get(id=self.cleaned_data['lua_en_id'])

        text_fr.code_name = self.cleaned_data.get('code_name')
        text_en.code_name = self.cleaned_data.get('code_name')

        text_fr.text = self.cleaned_data.get('text_fr')
        text_en.text = self.cleaned_data.get('text_en')

        text_fr.save()
        text_en.save()
        return text_fr
        # instance = super().save(commit)
        # learning_achievement_other_language = search(instance.learning_unit_year,
        #                                              instance.order)
        # if learning_achievement_other_language:
        #     learning_achievement_other_language.update(code_name=instance.code_name)
        #
        # # FIXME : We must have a English entry for each french entries
        # # Needs a refactoring of its model to include all languages in a single row.
        # if instance.language == language.find_by_code(FR_CODE_LANGUAGE):
        #     LearningAchievement.objects.get_or_create(learning_unit_year=instance.learning_unit_year,
        #                                               code_name=instance.code_name,
        #                                               language=language.find_by_code(EN_CODE_LANGUAGE))

        # return instance
