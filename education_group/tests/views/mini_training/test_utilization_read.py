from typing import List
from unittest import mock

from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse

from base.models.enums.education_group_types import MiniTrainingType
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.user import UserFactory
from education_group.views.mini_training.common_read import Tab
from program_management.ddd.domain.node import NodeGroupYear
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from program_management.tests.factories.element import ElementGroupYearFactory


class TestMLiniTrainingReadUtilization(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonWithPermissionsFactory('view_educationgroup')
        cls.mini_training_version = EducationGroupVersionFactory(
            offer__acronym="APPBIOL",
            offer__academic_year__year=2019,
            offer__education_group_type__name=MiniTrainingType.DEEPENING.name,
            root_group__partial_acronym="LBIOL100P",
            root_group__academic_year__year=2019,
            root_group__education_group_type__name=MiniTrainingType.DEEPENING.name,
        )
        ElementGroupYearFactory(group_year=cls.mini_training_version.root_group)

        cls.url = reverse('mini_training_utilization', kwargs={'year': 2019, 'code': 'LBIOL100P'})

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_case_mini_training_not_exists(self):
        dummy_url = reverse('mini_training_utilization', kwargs={'year': 2018, 'code': 'DUMMY100B'})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "mini_training/utilization_read.html")

    @mock.patch('program_management.ddd.service.tree_service.search_trees_using_node', return_value=[])
    def test_assert_context_data(self, mock_tree_service):
        response = self.client.get(self.url)

        self.assertTrue(mock_tree_service.called)
        self.assertEqual(response.context['person'], self.person)
        self.assertEqual(response.context['group_year'], self.mini_training_version.root_group)
        self.assertIsInstance(response.context['tree'], str)
        self.assertIsInstance(response.context['node'], NodeGroupYear)
        self.assertIsInstance(response.context['utilization_rows'], List)

    def test_assert_active_tabs_is_utilization_and_others_are_not_active(self):
        response = self.client.get(self.url)

        self.assertTrue(response.context['tab_urls'][Tab.UTILIZATION]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.IDENTIFICATION]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.CONTENT]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.GENERAL_INFO]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.SKILLS_ACHIEVEMENTS]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.ADMISSION_CONDITION]['active'])
