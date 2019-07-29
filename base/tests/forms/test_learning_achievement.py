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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from base.forms.learning_achievement import LearningAchievementEditForm
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.learning_achievement import LearningAchievementFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from reference.tests.factories.language import LanguageFactory


class TestLearningUnitEditionForm(TestCase):
    def setUp(self):
        self.language_fr = LanguageFactory(code="FR")
        self.language_en = LanguageFactory(code="EN")
        self.learning_unit_year = LearningUnitYearFactory(
            academic_year=create_current_academic_year()
        )

    def test_should_raise_validation_error_case_existing_code(self):
        LearningAchievementFactory(
            learning_unit_year=self.learning_unit_year,
            language=self.language_fr,
            code_name='TEST'
        )

        data = {
            'code_name': 'TEST',
            'lua_fr_id': 1,
            'lua_en_id': 2
        }
        form = LearningAchievementEditForm(
            luy=self.learning_unit_year,
            data=data
        )
        form.load_initial()
        self.assertFalse(form.is_valid(), form.errors)
        self.assertDictEqual(
            form.errors,
            {
                'code_name': [
                    _("This code already exists for this learning unit")
                ],
            }
        )