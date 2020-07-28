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
from django.test import SimpleTestCase

from education_group.ddd.domain import training, exception
from education_group.ddd.domain.service import calculate_end_postponement
from education_group.tests.ddd.factories.training import TrainingFactory


class TestCalculateEndPostponement(SimpleTestCase):
    def setUp(self):
        self.starting_academic_year_year = 2020
        self.mock_starting_academic_year = self._mock_starting_academic_year()
        self.mock_training_repository = self._mock_training_repository()

    def _mock_starting_academic_year(self) -> mock.Mock:
        starting_academic_year = mock.Mock(year=self.starting_academic_year_year)
        patcher = mock.patch("base.models.academic_year.starting_academic_year", return_value=starting_academic_year)
        mock_starting_academic_year = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_starting_academic_year

    def _mock_training_repository(self):
        patcher = mock.patch("education_group.ddd.repository.training.TrainingRepository", autospec=True)
        mock_training_repository = patcher.start()
        mock_training_repository.search.return_value = []
        mock_training_repository.get.side_effect = exception.TrainingNotFoundException
        self.addCleanup(patcher.stop)
        return mock_training_repository

    def test_should_return_starting_academic_year_plus_default_postponement_years_when_training_end_year_is_none(self):
        training_with_none_end_year = TrainingFactory(end_year=None)

        result = calculate_end_postponement.CalculateEndPostponement.calculate_year_of_end_postponement(
            training_with_none_end_year,
            self.mock_training_repository
        )
        self.assertEqual(
            self.starting_academic_year_year + calculate_end_postponement.DEFAULT_YEARS_TO_POSTPONE,
            result
        )

    def test_should_return_end_year_when_inferior_to_starting_academic_year_plus_default_postponement_years(self):
        training_with_inferior_end_year = TrainingFactory(
            end_year=self.starting_academic_year_year + calculate_end_postponement.DEFAULT_YEARS_TO_POSTPONE - 2,
            entity_identity__year=2018
        )

        result = calculate_end_postponement.CalculateEndPostponement.calculate_year_of_end_postponement(
            training_with_inferior_end_year,
            self.mock_training_repository
        )
        self.assertEqual(
            training_with_inferior_end_year.end_year,
            result
        )

    def test_should_return_year_of_last_training_equals_when_posterior_trainings_exists(self):
        training_2019 = TrainingFactory(end_year=None, entity_identity__year=2019)
        training_2020 = training.TrainingBuilder().copy_to_next_year(
            training_2019,
            self.mock_training_repository
        )
        training_2021 = TrainingFactory(
            entity_identity__acronym=training_2019.entity_id.acronym,
            entity_identity__year=2021
        )
        self.mock_training_repository.search.return_value = [training_2020, training_2021]

        result = calculate_end_postponement.CalculateEndPostponement.calculate_year_of_end_postponement(
            training_2019,
            self.mock_training_repository
        )
        self.assertEqual(training_2020.entity_id.year, result)
