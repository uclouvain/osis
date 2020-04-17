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
from unittest import mock

from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag

from base.ddd.utils.validation_message import BusinessValidationMessageList, BusinessValidationMessage
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.forms.tree.detach import DetachNodeForm
from program_management.tests.ddd.factories.node import NodeEducationGroupYearFactory, NodeLearningUnitYearFactory


@override_flag('education_group_update', active=True)
class TestDetachNodeView(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.person = PersonFactory()

    def setUp(self):
        self.tree = self.setUpTreeData()

        self.path_to_detach = "|".join([
            str(self.tree.root_node.pk),
            str(self.tree.root_node.children[0].child.pk)
        ])

        self.url = reverse("tree_detach_node", kwargs={'root_id': self.tree.root_node.pk}) + "?path=%s" % self.path_to_detach
        self.client.force_login(self.person.user)

        self._mock_fetch_tree()
        self._mock_perms()

    def _mock_fetch_tree(self):
        fetch_tree_patcher = mock.patch('program_management.ddd.repositories.load_tree.load', return_value=self.tree)
        fetch_tree_patcher.start()
        self.addCleanup(fetch_tree_patcher.stop)

    def _mock_perms(self):
        self.perm_patcher = mock.patch(
            "program_management.business.group_element_years.perms.is_eligible_to_detach_group_element_year",
            return_value=True
        )
        self.mocked_perm = self.perm_patcher.start()
        self.addCleanup(self.perm_patcher.stop)

    def setUpTreeData(self):
        """
           |BIR1BA
           |----LBIR150T (common-core)
                |---LBIR1110 (UE)
           |----LBIR101G (subgroup)
        """
        education_group = EducationGroupYearFactory(partial_acronym="BIR1BA")
        root_node = NodeEducationGroupYearFactory(node_id=education_group.pk, code=education_group.partial_acronym)
        common_core = NodeEducationGroupYearFactory(code="LBIR150T")
        learning_unit_node = NodeLearningUnitYearFactory(code='LBIR1110')
        subgroup = NodeEducationGroupYearFactory(code="LBIR101G")

        common_core.add_child(learning_unit_node)
        root_node.add_child(common_core)
        root_node.add_child(subgroup)
        return ProgramTree(root_node)
