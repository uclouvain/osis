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
from django.test import SimpleTestCase

from learning_unit.ddd.domain.learning_unit_year import LearningUnitYear


class TestInit(SimpleTestCase):

    def test_when_titles_are_none(self):
        obj = LearningUnitYear(
            common_title_fr=None,
            common_title_en=None,
            specific_title_fr=None,
            specific_title_en=None,
        )
        self.assertEqual(obj.common_title_fr, '')
        self.assertEqual(obj.common_title_en, '')
        self.assertEqual(obj.specific_title_fr, '')
        self.assertEqual(obj.specific_title_en, '')

    def test_all_only_specific_title_is_none(self):
        obj = LearningUnitYear(
            common_title_fr="Titre",
            common_title_en="Title",
            specific_title_fr=None,
            specific_title_en=None,
        )

        self.assertEqual(obj.full_title_fr, obj.common_title_fr)
        self.assertEqual(obj.full_title_en, obj.common_title_en)

    def test_all_only_titles_not_none(self):
        obj = LearningUnitYear(
            common_title_fr="Titre",
            common_title_en="Title",
            specific_title_fr="Titre specifique",
            specific_title_en="Specific title",
        )

        self.assertEqual(obj.full_title_fr, "{} - {}".format(obj.common_title_fr, obj.specific_title_fr))
        self.assertEqual(obj.full_title_en, "{} - {}".format(obj.common_title_en, obj.specific_title_en))
