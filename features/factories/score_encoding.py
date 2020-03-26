import random

import factory
from django.contrib.auth.models import Permission

from base.tests.factories.academic_calendar import AcademicCalendarExamSubmissionFactory
from base.tests.factories.exam_enrollment import ExamEnrollmentFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.offer_year_calendar import OfferYearCalendarFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.session_examen import SessionExamFactory
from base.tests.factories.student import StudentFactory


class ScoreEncodingFactory:
    def __init__(self):
        self.students = StudentFactory.create_batch(100)

        self.offers = OfferYearFactory.create_batch(5, academic_year__current=True)
        self.learning_units = LearningUnitYearFactory.create_batch(20, academic_year__current=True)
        self.program_managers = ProgramManagerFactory.create_batch(
            len(self.offers),
            offer_year=factory.Iterator(self.offers)
        )

        perm = Permission.objects.filter(codename="can_access_scoreencoding").first()
        for manager in self.program_managers:
            manager.person.user.user_permissions.add(perm)

        academic_calendar = AcademicCalendarExamSubmissionFactory(academic_year__current=True)
        session_exam_calendar = SessionExamCalendarFactory(academic_calendar=academic_calendar)

        for offer in self.offers:
            OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offer)
            learning_units = random.sample(self.learning_units, 5)
            students = random.sample(self.students, 20)
            offer_enrollments = OfferEnrollmentFactory.create_batch(
                len(students),
                offer_year=offer,
                education_group_year=None,
                student=factory.Iterator(students)
            )
            for lu in learning_units:
                lu_enrollments = LearningUnitEnrollmentFactory.create_batch(
                    len(offer_enrollments),
                    learning_unit_year=lu,
                    offer_enrollment=factory.Iterator(offer_enrollments)
                )
                session_exam = SessionExamFactory(
                    learning_unit_year=lu,
                    number_session=session_exam_calendar.number_session,
                    offer_year=offer
                )
                ExamEnrollmentFactory.create_batch(
                    len(lu_enrollments),
                    learning_unit_enrollment=factory.Iterator(lu_enrollments),
                    session_exam=session_exam
                )
