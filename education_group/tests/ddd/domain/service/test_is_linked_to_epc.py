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

from base.tests.factories.education_group_year import EducationGroupYearFactory
from education_group.ddd.domain.service import linked_to_epc
from education_group.tests.ddd.factories.training import TrainingFactory


class TestTrainingIsLInkedToEpc(TestCase):
    def test_should_return_true_when_training_is_linked_to_epc(self):
        training_linked_to_epc = self.create_training_linked_with_epc()

        self.assertTrue(
            linked_to_epc.TrainingIsLinkedToEpc.is_linked_to_epc(training_linked_to_epc)
        )

    def test_should_return_false_when_training_is_not_linked_to_epc(self):
        training_not_linked_to_epc = self.create_training_not_linked_with_epc()

        self.assertFalse(
            linked_to_epc.TrainingIsLinkedToEpc.is_linked_to_epc(training_not_linked_to_epc)
        )

    def create_training_linked_with_epc(self):
        education_group_year_db = EducationGroupYearFactory(linked_with_epc=True)
        training_linked_to_epc = TrainingFactory(
            entity_identity__acronym=education_group_year_db.acronym,
            entity_identity__year=education_group_year_db.academic_year.year
        )
        return training_linked_to_epc

    def create_training_not_linked_with_epc(self):
        education_group_year_db = EducationGroupYearFactory(linked_with_epc=False)
        training_not_linked_to_epc = TrainingFactory(
            entity_identity__acronym=education_group_year_db.acronym,
            entity_identity__year=education_group_year_db.academic_year.year
        )
        return training_not_linked_to_epc
