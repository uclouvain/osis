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
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.utils.translation import ugettext_lazy as _

from base.models.learning_achievement import LearningAchievement, search
from reference.models import language
from reference.models.language import EN_CODE_LANGUAGE, FR_CODE_LANGUAGE


class LearningAchievementEditForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(config_name='minimal_plus_headers'), required=False, label=_('Text'))

    class Meta:
        model = LearningAchievement
        fields = ['code_name', 'text']

    def __init__(self, data=None, initial=None, **kwargs):
        initial = initial or {}

        if data and data.get('language_code'):
            initial['language'] = language.find_by_code(data.get('language_code'))

        super().__init__(data, initial=initial, **kwargs)

        self._get_code_name_disabled_status()

        for key, value in initial.items():
            setattr(self.instance, key, value)

    def _get_code_name_disabled_status(self):
        if self.instance.pk and self.instance.language.code == EN_CODE_LANGUAGE:
            self.fields["code_name"].disabled = True

    def save(self, commit=True):
        instance = super().save(commit)
        learning_achievement_other_language = search(instance.learning_unit_year,
                                                     instance.order)
        if learning_achievement_other_language:
            learning_achievement_other_language.update(code_name=instance.code_name)

        # FIXME : We must have a English entry for each french entries
        # Needs a refactoring of its model to include all languages in a single row.
        if instance.language == language.find_by_code(FR_CODE_LANGUAGE):
            LearningAchievement.objects.get_or_create(learning_unit_year=instance.learning_unit_year,
                                                      code_name=instance.code_name,
                                                      language=language.find_by_code(EN_CODE_LANGUAGE))

        return instance
