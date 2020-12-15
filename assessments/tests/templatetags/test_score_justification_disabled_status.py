##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from assessments.templatetags.score_justification_disabled_status import get_score_justification_disabled_status, \
    DISABLED, ENABLED
from base.models.enums import exam_enrollment_state as enrollment_states
from base.models.enums.exam_enrollment_justification_type import CHEATING
from base.tests.factories.exam_enrollment import ExamEnrollmentFactory


class ScoreJustificationDisabledStatusForProgramManagerTests(TestCase):
    def setUp(self) -> None:
        self.exam_enrollment = ExamEnrollmentFactory()
        self.exam_enrollment.deadline_reached = False
        self.exam_enrollment.deadline_tutor_reached = False

    def test_enrollment_not_enrolled(self):
        self.exam_enrollment.enrollment_state = enrollment_states.NOT_ENROLLED
        context = {'is_program_manager': True, 'enrollment': self.exam_enrollment}
        self.assertEqual(get_score_justification_disabled_status(context), DISABLED)

    def test_enrollment_not_enrolled_deadline_reached(self):
        self.exam_enrollment.enrollment_state = enrollment_states.ENROLLED
        self.exam_enrollment.deadline_reached = True
        context = {'is_program_manager': True, 'enrollment': self.exam_enrollment}
        self.assertEqual(get_score_justification_disabled_status(context), DISABLED)

    def test_enrollment_not_enrolled_deadline_unreached(self):
        self.exam_enrollment.enrollment_state = enrollment_states.ENROLLED
        self.exam_enrollment.deadline_reached = False
        context = {'is_program_manager': True, 'enrollment': self.exam_enrollment}
        self.assertEqual(get_score_justification_disabled_status(context), ENABLED)


class ScoreJustificationDisabledStatusNotProgramManagerTests(TestCase):
    def setUp(self):
        self.context = {'is_program_manager': False}
        self.enrollment_enrolled = ExamEnrollmentFactory(enrollment_state=enrollment_states.ENROLLED)
        self.enrollment_enrolled.deadline_reached = False
        self.enrollment_enrolled.deadline_tutor_reached = False

    def test_enrollment_not_enrolled(self):
        self.enrollment_enrolled.enrollment_state = enrollment_states.NOT_ENROLLED
        self.context.update({'enrollment': self.enrollment_enrolled})
        self.assertEqual(get_score_justification_disabled_status(self.context), DISABLED)

    def test_enrollment_not_enrolled_deadline_reached(self):
        self.enrollment_enrolled.deadline_reached = True

        self.context.update({'enrollment': self.enrollment_enrolled})
        self.assertEqual(get_score_justification_disabled_status(self.context), DISABLED)

    def test_enrollment_not_enrolled_deadline_unreached(self):
        self.enrollment_enrolled.deadline_reached = False
        self.enrollment_enrolled.deadline_tutor_reached = False

        self.context.update({'enrollment': self.enrollment_enrolled})
        self.assertEqual(get_score_justification_disabled_status(self.context), ENABLED)

    def test_enrollment_score_final(self):
        self.enrollment_enrolled.score_final = 10

        self.context.update({'enrollment': self.enrollment_enrolled})
        self.assertEqual(get_score_justification_disabled_status(self.context), DISABLED)

    def test_enrollment_score_final_equal_to_0(self):
        self.enrollment_enrolled.score_final = 0

        self.context.update({'enrollment': self.enrollment_enrolled})
        self.assertEqual(get_score_justification_disabled_status(self.context), DISABLED)

    def test_enrollment_justification_final(self):
        self.enrollment_enrolled.justification_final = CHEATING

        self.context.update({'enrollment': self.enrollment_enrolled})
        self.assertEqual(get_score_justification_disabled_status(self.context), DISABLED)

    def test_enrollment_deadline_tutor_reached(self):

        self.enrollment_enrolled.deadline_reached = False
        self.enrollment_enrolled.deadline_tutor_reached = True
        self.context.update({'enrollment': self.enrollment_enrolled})
        self.assertEqual(get_score_justification_disabled_status(self.context), DISABLED)
