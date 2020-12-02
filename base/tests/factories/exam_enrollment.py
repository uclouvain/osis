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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import string

import factory.fuzzy
from faker import Faker

from base.models.enums import exam_enrollment_state
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.session_examen import SessionExamFactory
from osis_common.utils.datetime import get_tzinfo

fake = Faker()


class ExamEnrollmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'base.ExamEnrollment'

    external_id = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    changed = fake.date_time_this_decade(before_now=True, after_now=True, tzinfo=get_tzinfo())
    score_draft = None
    score_reencoded = None
    score_final = None
    justification_reencoded = None
    justification_final = None
    session_exam = factory.SubFactory(SessionExamFactory)
    learning_unit_enrollment = factory.SubFactory(LearningUnitEnrollmentFactory)
    enrollment_state = exam_enrollment_state.ENROLLED
    date_enrollment = None
