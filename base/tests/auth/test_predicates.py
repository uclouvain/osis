import mock
from django.test import TestCase

from base.auth.predicates import is_linked_to_offer
from base.auth.roles.program_manager import ProgramManager
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory


class TestUserIsLinkedToOffer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.education_group_year = EducationGroupYearFactory(academic_year=cls.academic_year)
        cls.person = PersonFactory()

    def setUp(self):
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'role_qs': ProgramManager.objects.filter(person=self.person),
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_user_manage_education_group(self):
        ProgramManagerFactory(person=self.person, education_group=self.education_group_year.education_group)
        self.assertTrue(is_linked_to_offer(self.person.user, self.education_group_year))

    def test_user_manager_another_education_group(self):
        ProgramManagerFactory(person=self.person, education_group=EducationGroupYearFactory().education_group)
        self.assertFalse(is_linked_to_offer(self.person.user, self.education_group_year))

    def test_predicate_without_permission_object(self):
        self.assertIsNone(is_linked_to_offer(self.person.user, None))
