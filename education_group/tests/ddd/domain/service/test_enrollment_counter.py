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
import mock
from django.test import SimpleTestCase

from education_group.ddd.domain.service.enrollment_counter import EnrollmentCounter
from education_group.ddd.domain.training import TrainingIdentity


class TestEnrollmentCounter(SimpleTestCase):
    @mock.patch('education_group.ddd.domain.service.enrollment_counter.EnrollmentCounter.'
                '_get_training_enrollments_count')
    def test_assert_training_called_when_instance_of_training_identity(self, mock_training_count):
        training_id = TrainingIdentity(acronym="DROI2M", year=2000)
        EnrollmentCounter().get_enrollments_count(training_id)

        self.assertTrue(mock_training_count.called)

    # @mock.patch('education_group.ddd.domain.service.enrollment_counter.EnrollmentCounter.'
    #             '_get_mini_training_enrollments_count')
    # def test_assert_mini_training_called_when_instance_of_mini_training_identity(self, mock_mini_training_count):
    #     mini_training_id = MiniTrainingIdentity(acronym="DROI2M", year=2000)
    #     EnrollmentCounter().get_enrollments_count(mini_training_id)
    #
    #     self.assertTrue(mock_mini_training_count.called)

    def test_assert_raise_exception_when_entity_id_type_not_supported(self):
        with self.assertRaises(Exception):
            EnrollmentCounter().get_enrollments_count(None)
