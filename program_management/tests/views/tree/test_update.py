# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from unittest import mock

from django.http import HttpResponse, HttpResponseForbidden
from django.test import TestCase
from django.urls import reverse
from mock import patch

from base.tests.factories.person import PersonFactory
from education_group.tests.factories.group_year import GroupYearFactory
from osis_role.contrib.views import AjaxPermissionRequiredMixin
from program_management.forms.tree.paste import PasteNodesFormset
from program_management.forms.tree.update import UpdateNodeForm
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory, \
    NodeGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory


def form_valid_effect(formset: PasteNodesFormset):
    for form in formset:
        form.cleaned_data = {}
    return True


class TestUpdateLinkView(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.person = PersonFactory()

    def setUp(self):
        self.tree = self.setUpTreeData()
        self.parent = self.tree.root_node
        self.child = self.tree.root_node.children_as_nodes[0]
        self.url = reverse("tree_update_link", args=[
            self.parent.code, self.parent.year, self.child.code, self.child.year
        ])
        self.client.force_login(self.person.user)
        self.setUpPatchers()

    def setUpPatchers(self):
        get_tree_patcher = mock.patch(
            'program_management.ddd.service.read.get_program_tree_service.get_program_tree',
            return_value=self.tree
        )
        self.get_tree_patcher_mock = get_tree_patcher.start()
        self.addCleanup(get_tree_patcher.stop)

        get_link_patcher = mock.patch(
            'program_management.ddd.domain.program_tree.ProgramTree.get_first_link_occurence_using_node',
            return_value=LinkFactory(parent=self.parent, child=self.child)
        )
        self.get_link_patcher_mock = get_link_patcher.start()
        self.addCleanup(get_tree_patcher.stop)

        get_perm_object_patcher = mock.patch(
            'program_management.views.tree.update.UpdateLinkView.get_permission_object',
            return_value=GroupYearFactory(
                partial_acronym=self.tree.root_node.code, academic_year__year=self.tree.root_node.year
            )
        )
        get_perm_object_patcher.start()
        self.addCleanup(get_perm_object_patcher.stop)

        get_node_patcher = mock.patch(
            'program_management.ddd.repositories.node.NodeRepository.get',
            return_value=self.child
        )
        self.get_node_patcher_mock = get_node_patcher.start()
        self.addCleanup(get_node_patcher.stop)

        permission_patcher = mock.patch.object(AjaxPermissionRequiredMixin, "has_permission")
        self.permission_mock = permission_patcher.start()
        self.permission_mock.return_value = True
        self.addCleanup(permission_patcher.stop)

    def setUpTreeData(self):
        """
           |BIR1BA
           |----LBIR150T (common-core)
        """
        root_node = NodeGroupYearFactory(code="BIR1BA")
        common_core = NodeGroupYearFactory(code="LBIR150T")
        root_node.add_child(common_core)
        return ProgramTreeFactory(root_node=root_node)

    def test_should_return_form_when_update_action_is_chosen(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'tree/link_update_inner.html')
        self.assertIsInstance(response.context['form'], UpdateNodeForm)

    def test_should_show_access_denied_when_user_has_not_perm(self):
        self.permission_mock.return_value = False
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_should_show_form_template_according_to_parent_child_link(self):
        self._should_show_group_form()
        self._should_show_learning_unit_form()
        self._should_show_minor_major_option_form()

    def _should_show_group_form(self):
        self.get_node_patcher_mock.return_value = NodeGroupYearFactory()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'blocks/link_form_inner/group_inner.html')

    def _should_show_learning_unit_form(self):
        self.get_node_patcher_mock.return_value = NodeLearningUnitYearFactory()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'blocks/link_form_inner/learning_unit_inner.html')

    def _should_show_minor_major_option_form(self):
        self.get_tree_patcher_mock.return_value = ProgramTreeFactory(root_node=NodeGroupYearFactory(listchoice=True))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'blocks/link_form_inner/minor_major_option_inner.html')
