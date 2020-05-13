import mock
from django.test import TestCase, override_settings

from base.models.enums.education_group_types import TrainingType
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from education_group.auth import predicates
from education_group.auth.roles.faculty_manager import FacultyManager
from education_group.auth.scope import Scope
from education_group.tests.factories.auth.faculty_manager import FacultyManagerFactory


class TestUserAttachedToManagementEntity(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_entity_version = EntityVersionFactory(parent=None)
        cls.entity_version_level_1 = EntityVersionFactory(parent=cls.root_entity_version.entity)
        cls.entity_version_level_2 = EntityVersionFactory(parent=cls.entity_version_level_1.entity)

        cls.academic_year = AcademicYearFactory(current=True)
        cls.education_group_year = EducationGroupYearFactory(
            academic_year=cls.academic_year,
            management_entity=cls.entity_version_level_1.entity
        )
        cls.person = PersonFactory()

    def setUp(self):
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'role_qs': FacultyManager.objects.filter(person=self.person),
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_user_manage_only_entity_of_education_group_year(self):
        FacultyManagerFactory(
            person=self.person,
            entity=self.entity_version_level_1.entity,
            with_child=False
        )
        self.assertTrue(predicates.is_user_attached_to_management_entity(self.person.user, self.education_group_year))

    def test_user_manage_entity_and_child_of_education_group_year(self):
        FacultyManagerFactory(
            person=self.person,
            entity=self.entity_version_level_1.entity,
            with_child=True
        )
        self.assertTrue(predicates.is_user_attached_to_management_entity(self.person.user, self.education_group_year))

    def test_user_manage_only_parent_entity_of_education_group_year(self):
        FacultyManagerFactory(
            person=self.person,
            entity=self.root_entity_version.entity,
            with_child=False
        )
        self.assertFalse(predicates.is_user_attached_to_management_entity(self.person.user, self.education_group_year))

    def test_user_manage_parent_entity_and_its_children_which_are_management_entity_education_group_year(self):
        FacultyManagerFactory(
            person=self.person,
            entity=self.root_entity_version.entity,
            with_child=True
        )
        self.assertTrue(predicates.is_user_attached_to_management_entity(self.person.user, self.education_group_year))

    def test_user_manage_multiple_entity_but_none_are_management_entity_of_education_group_year(self):
        new_entity_version = EntityVersionFactory(parent=self.root_entity_version.entity)

        for entity in [self.root_entity_version.entity, new_entity_version.entity]:
            FacultyManagerFactory(person=self.person, entity=entity, with_child=False)

        self.assertFalse(predicates.is_user_attached_to_management_entity(self.person.user, self.education_group_year))


class TestEducationGroupYearOlderOrEqualsThanLimitSettings(TestCase):
    def setUp(self):
        self.user = UserFactory.build()
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    @override_settings(YEAR_LIMIT_EDG_MODIFICATION=2018)
    def test_education_group_year_older_than_settings(self):
        education_group_year = EducationGroupYearFactory.build(academic_year__year=2019)
        self.assertTrue(predicates.is_education_group_year_older_or_equals_than_limit_settings_year(
            self.user,
            education_group_year
        ))

    @override_settings(YEAR_LIMIT_EDG_MODIFICATION=2018)
    def test_education_group_year_earlier_than_settings(self):
        education_group_year = EducationGroupYearFactory.build(academic_year__year=2017)
        self.assertFalse(predicates.is_education_group_year_older_or_equals_than_limit_settings_year(
            self.user,
            education_group_year
        ))

    @override_settings(YEAR_LIMIT_EDG_MODIFICATION=2018)
    def test_education_group_year_equals_to_settings(self):
        education_group_year = EducationGroupYearFactory.build(academic_year__year=2018)
        self.assertTrue(predicates.is_education_group_year_older_or_equals_than_limit_settings_year(
            self.user,
            education_group_year
        ))


class TestEducationGroupTypeAuthorizedAccordingToScope(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()

    def setUp(self):
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'role_qs': FacultyManager.objects.filter(person=self.person),
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_case_user_have_sufficient_scope_to_manage_education_group_type(self):
        education_group_type_managed = EducationGroupYearFactory(
            education_group_type__name=TrainingType.CERTIFICATE_OF_SUCCESS.name
        )
        FacultyManagerFactory(person=self.person, scopes=[Scope.IUFC.name],)

        self.assertTrue(
            predicates.is_education_group_type_authorized_according_to_user_scope(
                self.person.user,
                education_group_type_managed
            )
        )

    def test_case_user_dont_have_sufficient_scope_to_manage_education_group_type(self):
        education_group_type_managed = EducationGroupYearFactory(
            education_group_type__name=TrainingType.BACHELOR.name
        )
        FacultyManagerFactory(person=self.person, scopes=[Scope.IUFC.name],)

        self.assertFalse(
            predicates.is_education_group_type_authorized_according_to_user_scope(
                self.person.user,
                education_group_type_managed
            )
        )


class TestIsEditionProgramPeriodOpen(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.education_group_year = EducationGroupYearFactory()

    def setUp(self):
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    @mock.patch('base.business.event_perms.EventPermEducationGroupEdition.is_open', return_value=True)
    def test_case_edition_program_period_open(self, mock_event_perm_is_open):
        self.assertTrue(
            predicates.is_program_edition_period_open(
                self.user,
                self.education_group_year
            )
        )

    @mock.patch('base.business.event_perms.EventPermEducationGroupEdition', return_value=False)
    def test_case_edition_program_period_closed(self, mock_event_perm_is_open):
        self.assertFalse(
            predicates.is_program_edition_period_open(
                self.user,
                self.education_group_year
            )
        )


class TestIsNotOrphanGroup(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.build()

    def setUp(self):
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_is_not_orphan_group_case_education_group_year_set(self):
        education_group_year = EducationGroupYearFactory.build()
        self.assertTrue(
            predicates.is_not_orphan_group(self.user, education_group_year)
        )

    def test_is_not_orphan_group_case_education_is_not_set(self):
        self.assertFalse(predicates.is_not_orphan_group(self.user))


class TestIsMaximumChildNotReachedForGroupCategory(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.build()
        cls.education_group_year = EducationGroupYearFactory()

    def setUp(self):
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_case_education_group_year_not_specified(self):
        message = "Predicate must return 'None' because not evaluated by permission engine when return value is 'None'"
        self.assertIsNone(
            predicates.is_maximum_child_not_reached_for_group_category(self.user),
            msg=message
        )

    @mock.patch('django.db.models.QuerySet.exists', return_value=False)
    def test_case_education_group_year_have_reach_limit_for_groups(self, mock_exist):
        self.assertFalse(
            predicates.is_maximum_child_not_reached_for_group_category(self.user, self.education_group_year)
        )

    @mock.patch('django.db.models.QuerySet.exists', return_value=True)
    def test_case_education_group_year_have_not_reach_limit_for_groups(self, mock_exist):
        self.assertTrue(
            predicates.is_maximum_child_not_reached_for_group_category(self.user, self.education_group_year)
        )


class TestIsMaximumChildNotReachedForMiniTrainingCategory(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.build()
        cls.education_group_year = EducationGroupYearFactory()

    def setUp(self):
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_case_education_group_year_not_specified(self):
        message = "Predicate must return 'None' because not evaluated by permission engine when return value is 'None'"
        self.assertIsNone(
            predicates.is_maximum_child_not_reached_for_mini_training_category(self.user),
            msg=message
        )

    @mock.patch('django.db.models.QuerySet.exists', return_value=False)
    def test_case_education_group_year_have_reach_limit_for_groups(self, mock_exist):
        self.assertFalse(
            predicates.is_maximum_child_not_reached_for_mini_training_category(self.user, self.education_group_year)
        )

    @mock.patch('django.db.models.QuerySet.exists', return_value=True)
    def test_case_education_group_year_have_not_reach_limit_for_groups(self, mock_exist):
        self.assertTrue(
            predicates.is_maximum_child_not_reached_for_mini_training_category(self.user, self.education_group_year)
        )


class TestIsMaximumChildNotReachedForTrainingCategory(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.build()
        cls.education_group_year = EducationGroupYearFactory()

    def setUp(self):
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_case_education_group_year_not_specified(self):
        message = "Predicate must return 'None' because not evaluated by permission engine when return value is 'None'"
        self.assertIsNone(
            predicates.is_maximum_child_not_reached_for_training_category(self.user),
            msg=message
        )

    @mock.patch('django.db.models.QuerySet.exists', return_value=False)
    def test_case_education_group_year_have_reach_limit_for_groups(self, mock_exist):
        self.assertFalse(
            predicates.is_maximum_child_not_reached_for_training_category(self.user, self.education_group_year)
        )

    @mock.patch('django.db.models.QuerySet.exists', return_value=True)
    def test_case_education_group_year_have_not_reach_limit_for_groups(self, mock_exist):
        self.assertTrue(
            predicates.is_maximum_child_not_reached_for_training_category(self.user, self.education_group_year)
        )