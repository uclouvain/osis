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
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from education_group.ddd.business_types import *
from education_group.ddd.domain.service import has_inscriptions
from education_group.tests.ddd.factories.training import TrainingFactory


class TestTrainingHasInscriptions(TestCase):
    def test_should_return_false_when_training_has_inscriptions(self):
        training_with_inscriptions = self.create_training_with_inscriptions()

        self.assertTrue(
            has_inscriptions.TrainingHasInscriptions.has_inscriptions(training_with_inscriptions)
        )

    def test_should_return_true_when_training_has_no_inscriptions(self):
        training_without_inscriptions = self.create_training_without_inscriptions()

        self.assertFalse(
            has_inscriptions.TrainingHasInscriptions.has_inscriptions(training_without_inscriptions)
        )

    def create_training_with_inscriptions(self) -> 'Training':
        education_group_year_db = EducationGroupYearFactory()
        OfferEnrollmentFactory(education_group_year=education_group_year_db)
        training_with_inscriptions = TrainingFactory(
            entity_identity__acronym=education_group_year_db.acronym,
            entity_identity__year=education_group_year_db.academic_year.year
        )
        return training_with_inscriptions

    def create_training_without_inscriptions(self) -> 'Training':
        education_group_year_db = EducationGroupYearFactory()
        training_without_inscriptions = TrainingFactory(
            entity_identity__acronym=education_group_year_db.acronym,
            entity_identity__year=education_group_year_db.academic_year.year
        )
        return training_without_inscriptions

