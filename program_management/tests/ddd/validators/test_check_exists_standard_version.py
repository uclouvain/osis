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
import attr
from django.test import SimpleTestCase

from program_management.ddd.validators import _check_exists_standard_version
from program_management.tests.ddd.factories.program_tree_version import SpecificProgramTreeVersionFactory, \
    ProgramTreeVersionFactory, StandardProgramTreeVersionFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_version_repository
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin


class TestCheckExistsStandardVersionValidatorTest(SimpleTestCase, TestValidatorValidateMixin):
    def setUp(self):
        self.specific_version = SpecificProgramTreeVersionFactory()
        self.fake_version_repo = get_fake_program_tree_version_repository(
            [self.specific_version]
        )

    def test_should_not_be_valid_when_standard_version_not_exist_next_year(self):
        validator = _check_exists_standard_version.CheckExistsStandardVersionValidator(
            self.specific_version,
            self.fake_version_repo
        )

        self.assertValidatorRaises(validator, None)

    def test_should_be_valid_when_standard_version_exists_next_year(self):
        self._create_next_year_standard_version()

        validator = _check_exists_standard_version.CheckExistsStandardVersionValidator(
            self.specific_version,
            self.fake_version_repo
        )

        self.assertValidatorNotRaises(validator)

    def test_should_be_valid_when_tree_version_is_already_standard(self):
        standard_tree = StandardProgramTreeVersionFactory()

        validator = _check_exists_standard_version.CheckExistsStandardVersionValidator(
            standard_tree,
            self.fake_version_repo
        )

        self.assertValidatorNotRaises(validator)

    def _create_next_year_standard_version(self):
        standard_tree_next_year = ProgramTreeVersionFactory(
            entity_id=attr.evolve(
                self.specific_version.entity_id,
                version_name="",
                year=self.specific_version.entity_id.year+1
            )
        )
        self.fake_version_repo.root_entities.append(standard_tree_next_year)