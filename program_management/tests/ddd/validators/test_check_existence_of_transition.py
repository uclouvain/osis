# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################

from django.test import TestCase

from program_management.ddd.validators import _update_check_existence_of_transition
from program_management.tests.ddd.factories.program_tree_version import StandardTransitionProgramTreeVersionFactory
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory


class CheckExistenceOfTransitionTest(TestCase, TestValidatorValidateMixin):
    @classmethod
    def setUpTestData(cls):
        start_year = 2020
        cls.initial_end_year = 2022
        cls.transition_version = StandardTransitionProgramTreeVersionFactory(
            start_year=start_year, end_year_of_existence=2026, entity_id__year=start_year
        )

    def test_should_be_valid_when_no_transition_in_future(self):
        validator = _update_check_existence_of_transition.CheckExistenceOfTransitionValidator(
            self.transition_version, self.initial_end_year
        )

        self.assertValidatorNotRaises(validator)

    def test_should_be_valid_when_no_version_exists_during_the_standard_year(self):
        self._create_transition_version_in_future()

        validator = _update_check_existence_of_transition.CheckExistenceOfTransitionValidator(
            self.transition_version, self.initial_end_year
        )

        self.assertValidatorRaises(validator, None)

    def _create_transition_version_in_future(self):
        EducationGroupVersionFactory(
            offer__acronym=self.transition_version.entity_id.offer_acronym,
            root_group__academic_year__year=self.transition_version.entity_id.year + 3,
            is_transition=True,
            version_name=self.transition_version.version_name
        )
