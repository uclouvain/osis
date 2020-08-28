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
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseNotFound, HttpResponse
from django.test import TestCase, override_settings
from requests import Timeout

from base.business.education_groups import general_information
from base.business.education_groups.general_information import PublishException, _bulk_publish, \
    _get_code_computed_according_type
from base.models.enums.education_group_types import MiniTrainingType, TrainingType
from program_management.tests.ddd.factories.node import NodeGroupYearFactory


@override_settings(ESB_API_URL="api.esb.com",
                   ESB_AUTHORIZATION="Basic dummy:1234",
                   ESB_REFRESH_PEDAGOGY_ENDPOINT="offer/{year}/{code}/refresh",
                   ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT='offer/{year}/common/refresh',
                   ESB_REFRESH_COMMON_ADMISSION_ENDPOINT='offer/{year}/common_admission/refresh')
class TestPublishGeneralInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.node = NodeGroupYearFactory(node_type=TrainingType.PGRM_MASTER_120)

    def setUp(self):
        self.get_pgrm_trees_patcher = mock.patch("base.business.education_groups.general_information."
                                                 "search_program_trees_using_node_service."
                                                 "search_program_trees_using_node",
                                                 return_value=[])
        self.mocked_get_pgrm_trees = self.get_pgrm_trees_patcher.start()
        self.addCleanup(self.get_pgrm_trees_patcher.stop)

    @override_settings(ESB_REFRESH_PEDAGOGY_ENDPOINT=None)
    def test_publish_case_missing_settings(self):
        with self.assertRaises(ImproperlyConfigured):
            general_information.publish_group_year(self.node.code, self.node.year)

    @mock.patch('requests.get', return_value=HttpResponse)
    @mock.patch('threading.Thread')
    def test_publish_call_seperate_thread(self, mock_thread, mock_get):
        mock_thread.start.return_value = True
        general_information.publish_group_year(self.node.code, self.node.year)
        self.assertTrue(mock_thread.start)

    @mock.patch('requests.get', return_value=HttpResponseNotFound)
    def test_publish_case_not_found_return_false(self, mock_requests):
        dummy_url = 'dummy_url'
        response = general_information._publish(dummy_url, self.node.code, self.node.year)
        self.assertIsInstance(response, bool)
        self.assertFalse(response)

    @mock.patch('requests.get', side_effect=Timeout)
    def test_publish_case_timout_reached(self, mock_requests):
        dummy_url = 'dummy_url'
        with self.assertRaises(PublishException):
            general_information._publish(dummy_url, self.node.code, self.node.year)

    @mock.patch('requests.get', return_value=HttpResponse)
    def test_publish_case_success(self, mock_requests):
        dummy_url = 'dummy_url'
        response = general_information._publish(dummy_url, self.node.code, self.node.year)
        self.assertIsInstance(response, bool)
        self.assertTrue(response)


@override_settings(ESB_API_URL="api.esb.com",
                   ESB_AUTHORIZATION="Basic dummy:1234",
                   ESB_REFRESH_PEDAGOGY_ENDPOINT="offer/{year}/{code}/refresh",
                   ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT='offer/{year}/common/refresh',
                   ESB_REFRESH_COMMON_ADMISSION_ENDPOINT='offer/{year}/common_admission/refresh')
class TestBulkPublish(TestCase):
    @mock.patch('base.business.education_groups.general_information._publish', return_value=True)
    def test_bulk_publish_assert_call_publish(self, mock_publish):
        node_1 = NodeGroupYearFactory(node_type=TrainingType.PGRM_MASTER_120)
        node_2 = NodeGroupYearFactory(node_type=TrainingType.PGRM_MASTER_180_240)

        _bulk_publish([node_1, node_2])
        self.assertTrue(mock_publish.called)


class TestGetCodeComputedAccordingType(TestCase):
    def test_assert_minor_code_computed(self):
        node = NodeGroupYearFactory(title="MINOR", node_type=MiniTrainingType.ACCESS_MINOR)

        expected_computed_code = "min-{}".format(node.code)
        self.assertEqual(
            _get_code_computed_according_type(node),
            expected_computed_code
        )

    def test_assert_deepening_code_computed(self):
        node = NodeGroupYearFactory(title="DEEPENING", node_type=MiniTrainingType.DEEPENING)

        expected_computed_code = "app-{}".format(node.code)
        self.assertEqual(
            _get_code_computed_according_type(node),
            expected_computed_code
        )

    def test_assert_major_code_computed(self):
        node = NodeGroupYearFactory(title="MAJOR", node_type=MiniTrainingType.FSA_SPECIALITY)

        expected_computed_code = "fsa1ba-{}".format(node.code)
        self.assertEqual(
            _get_code_computed_according_type(node),
            expected_computed_code
        )
