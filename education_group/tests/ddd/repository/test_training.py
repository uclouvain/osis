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

from django.test import TestCase

from base.models.education_group_year import EducationGroupYear
from base.tests.factories.education_group_year import TrainingFactory
from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.repository.training import TrainingRepository


class TestTrainingRepositoryDeleteMethod(TestCase):
    def setUp(self) -> None:
        self.training_db = TrainingFactory()

    def test_assert_delete_in_database(self):
        training_id = TrainingIdentity(acronym=self.training_db.acronym, year=self.training_db.academic_year.year)
        TrainingRepository.delete(training_id)

        with self.assertRaises(EducationGroupYear.DoesNotExist):
            EducationGroupYear.objects.get(acronym=training_id.acronym, academic_year__year=training_id.year)
