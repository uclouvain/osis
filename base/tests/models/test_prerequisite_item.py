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

from django.test import TestCase

from base.models import prerequisite_item
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.prerequisite import PrerequisiteFactory
from base.tests.factories.prerequisite_item import PrerequisiteItemFactory


class TestPrerequisiteItem(TestCase):
    def setUp(self):
        self.learning_unit_is_prerequisite = LearningUnitFactory()
        self.learning_unit_not_prerequisite = LearningUnitFactory()
        self.learning_unit_year_with_prerequisite = LearningUnitYearFactory()
        self.learning_unit_year_without_prerequisite = LearningUnitYearFactory()
        self.prerequisite = PrerequisiteFactory(learning_unit_year=self.learning_unit_year_with_prerequisite)
        self.prerequisite_item = PrerequisiteItemFactory(
            prerequisite=self.prerequisite,
            learning_unit=self.learning_unit_is_prerequisite
        )

    def test_find_by_learning_unit_year_having_prerequisite(self):
        self.assertEqual(
            list(prerequisite_item.find_by_learning_unit_year_having_prerequisite(
                self.learning_unit_year_with_prerequisite)),
            [self.prerequisite_item]
        )
        self.assertFalse(
            list(prerequisite_item.find_by_learning_unit_year_having_prerequisite(
                self.learning_unit_year_without_prerequisite))
        )

    def test_find_by_learning_unit_being_prerequisite(self):
        self.assertEqual(
            list(
                prerequisite_item.find_by_learning_unit_being_prerequisite(
                    self.learning_unit_is_prerequisite
                )
            ),
            [self.prerequisite_item]
        )
        self.assertFalse(
            list(
                prerequisite_item.find_by_learning_unit_being_prerequisite(
                    self.learning_unit_not_prerequisite
                )
            )
        )
