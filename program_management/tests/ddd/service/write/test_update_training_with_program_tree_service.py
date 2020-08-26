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
import mock
from django.test import TestCase

from education_group.ddd.domain import training, group
from education_group.tests.ddd.factories.command.update_training_factory import UpdateTrainingCommandFactory
from education_group.tests.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.repository.fake import get_fake_group_repository, get_fake_training_repository
from education_group.tests.ddd.factories.training import TrainingFactory
from program_management.ddd.domain import program_tree, program_tree_version
from program_management.ddd.domain.program_tree_version import STANDARD
from program_management.ddd.service.write import update_training_with_program_tree_service
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_repository, \
    get_fake_program_tree_version_repository
from testing.mocks import MockPatcherMixin


@mock.patch("education_group.ddd.domain.service.calculate_end_postponement."
            "CalculateEndPostponement.calculate_year_of_postponement", return_value=2021)
class TestUpdateAndReportTrainingWithProgramTree(MockPatcherMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.code = "CODE"
        cls.acronym = "ACRON"

        cls.cmd = UpdateTrainingCommandFactory(
            code=cls.code,
            abbreviated_title=cls.acronym,
            year=2018
        )

    def setUp(self):
        self.trainings = [
            TrainingFactory(code=self.code, entity_identity__acronym=self.acronym, entity_identity__year=year)
            for year in range(2018, 2020)
        ]
        self.fake_training_repository = get_fake_training_repository(self.trainings)

        self.groups = [
            GroupFactory(abbreviated_title=self.acronym, entity_identity__code=self.code, entity_identity__year=year)
            for year in range(2018, 2020)
        ]
        self.fake_group_repository = get_fake_group_repository(self.groups)

        self.program_trees = [
            ProgramTreeFactory(root_node__code=self.code, root_node__title=self.acronym, root_node__year=year)
            for year in range(2018, 2020)
        ]
        self.fake_program_tree_repository = get_fake_program_tree_repository(self.program_trees)

        self.program_tree_versions = [
            ProgramTreeVersionFactory(tree=tree, entity_id__version_name=STANDARD, program_tree_repository=self.fake_program_tree_repository)
            for tree in self.program_trees
        ]
        self.fake_program_tree_version_repository = get_fake_program_tree_version_repository(self.program_tree_versions)

        self.mock_repo("education_group.ddd.repository.group.GroupRepository", self.fake_group_repository)
        self.mock_repo("education_group.ddd.repository.training.TrainingRepository", self.fake_training_repository)
        self.mock_repo(
            "program_management.ddd.repositories.program_tree.ProgramTreeRepository",
            self.fake_program_tree_repository
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository",
            self.fake_program_tree_version_repository
        )

    def test_should_return_training_identities(self, mock_postponement_end_year):
        result = update_training_with_program_tree_service.update_and_report_training_with_program_tree(self.cmd)

        expected_result = [
            training.TrainingIdentity(acronym=self.acronym, year=year) for year in range(2018, 2022)
        ]
        self.assertListEqual(expected_result, result)

    def test_should_postpone_groups(self, mock_postponement_end_year):
        update_training_with_program_tree_service.update_and_report_training_with_program_tree(self.cmd)

        group_identities = [
            group.GroupIdentity(code=self.code, year=year) for year in range(2018, 2022)
        ]

        base_group = self.fake_group_repository.get(group_identities[0])

        for identity in group_identities[1:]:
            with self.subTest(year=identity.year):
                postponed_group = self.fake_group_repository.get(identity)
                self.assertTrue(postponed_group.has_same_values_as(base_group))

    def test_should_postpone_trainings(self, mock_postponement_end_year):
        training_identities = update_training_with_program_tree_service.update_and_report_training_with_program_tree(
            self.cmd
        )

        base_training = self.fake_training_repository.get(training_identities[0])

        for identity in training_identities[1:]:
            with self.subTest(year=identity.year):
                postponed_training = self.fake_training_repository.get(identity)
                self.assertTrue(postponed_training.has_same_values_as(base_training))

    def test_should_postpone_program_tree(self, mock_postponement_end_year):
        update_training_with_program_tree_service.update_and_report_training_with_program_tree(self.cmd)

        program_tree_identities = [
            program_tree.ProgramTreeIdentity(code=self.code, year=year) for year in range(2018, 2022)
        ]

        for identity in program_tree_identities:
            with self.subTest(year=identity.year):
                self.assertTrue(self.fake_program_tree_repository.get(identity))

    def test_should_postpone_program_tree_version(self, mock_postponement_end_year):
        update_training_with_program_tree_service.update_and_report_training_with_program_tree(self.cmd)

        program_tree_version_identities = [
            program_tree_version.ProgramTreeVersionIdentity(
                offer_acronym=self.acronym,
                year=year,
                version_name="",
                is_transition=False
            ) for year in range(2018, 2022)
        ]

        for identity in program_tree_version_identities:
            with self.subTest(year=identity.year):
                self.assertTrue(self.fake_program_tree_version_repository.get(identity))
