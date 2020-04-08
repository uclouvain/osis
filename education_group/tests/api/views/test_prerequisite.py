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

from django.conf import settings
from django.test import RequestFactory
from django.urls import reverse
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from base.models.enums import prerequisite_operator
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from education_group.api.serializers.prerequisite import EducationGroupPrerequisitesSerializerLearningUnit
from program_management.ddd.domain import prerequisite
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory


class TrainingPrerequisitesTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()

    def setUp(self):
        """
        root_node
        |-----common_core
             |---- LDROI100A (UE)
        |----subgroup1
             |---- LDROI120B (UE)
             |----subgroup2
                  |---- LDROI100A (UE)
        :return:
        """
        self.root_node = NodeGroupYearFactory(node_id=1, code="LBIR100B", title="Bachelier en droit", year=2018)
        self.common_core = NodeGroupYearFactory(node_id=2, code="LGROUP100A", title="Tronc commun", year=2018)
        self.ldroi100a = NodeLearningUnitYearFactory(node_id=3, code="LDROI100A", title="Introduction", year=2018)
        self.ldroi120b = NodeLearningUnitYearFactory(node_id=4, code="LDROI120B", title="Séminaire", year=2018)
        self.subgroup1 = NodeGroupYearFactory(node_id=5, code="LSUBGR100G", title="Sous-groupe 1", year=2018)
        self.subgroup2 = NodeGroupYearFactory(node_id=6, code="LSUBGR150G", title="Sous-groupe 2", year=2018)

        self.ldroi1300 = NodeLearningUnitYearFactory(node_id=7, code="LDROI1300", title="Introduction droit", year=2018)
        self.lagro2400 = NodeLearningUnitYearFactory(node_id=8, code="LAGRO2400", title="Séminaire agro", year=2018)

        self.root_egy = EducationGroupYearFactory(id=self.root_node.node_id,
                                                  acronym=self.root_node.code,
                                                  title=self.root_node.title,
                                                  academic_year__year=self.root_node.year)

        LinkFactory(parent=self.root_node, child=self.common_core)
        LinkFactory(parent=self.common_core, child=self.ldroi100a)
        LinkFactory(parent=self.root_node, child=self.subgroup1)
        LinkFactory(parent=self.subgroup1, child=self.ldroi120b)
        LinkFactory(parent=self.subgroup1, child=self.subgroup2)
        LinkFactory(parent=self.subgroup2, child=self.ldroi100a)

        self.p_group = prerequisite.PrerequisiteItemGroup(operator=prerequisite_operator.AND)
        self.p_group.add_prerequisite_item('LDROI1300', 2018)
        self.p_group.add_prerequisite_item('LAGRO2400', 2018)

        p_req = prerequisite.Prerequisite(main_operator=prerequisite_operator.AND)
        p_req.add_prerequisite_item_group(self.p_group)
        self.ldroi100a.set_prerequisite(p_req)

        self.tree = ProgramTree(root_node=self.root_node)

        self.url = reverse('education_group_api_v1:training-prerequisites', kwargs={'year': self.root_node.year,
                                                                                    'acronym': self.root_node.code})
        self.request = RequestFactory().get(self.url)
        self.serializer = EducationGroupPrerequisitesSerializerLearningUnit(self.ldroi100a, context={
            'request': self.request,
            'language': settings.LANGUAGE_CODE_EN,
            'tree': self.tree
        })
        self.client.force_authenticate(user=self.person.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put', 'patch']

        for method in methods_not_allowed:
            with self.subTest(method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_results_case_education_group_year_not_found(self):
        invalid_url = reverse('education_group_api_v1:training-prerequisites', kwargs={
            'acronym': 'ACRO',
            'year': 2019
        })
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('education_group.api.views.prerequisite.TrainingPrerequisites.get_queryset')
    def test_get_results(self, mock_get_queryset):
        mock_get_queryset.return_value = self.tree.get_nodes_that_have_prerequisites()
        response = self.client.get(self.url)
        with self.subTest('Test status code'):
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest('Test response'):
            self.assertEqual([self.serializer.data], response.json())
