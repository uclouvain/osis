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

import random

import mock
from django.test import SimpleTestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.models.enums import link_type
from base.models.enums.education_group_types import TrainingType
from base.models.enums.proposal_type import ProposalType
from base.utils.urls import reverse_with_get
from program_management.models.enums.node_type import NodeType
from program_management.serializers.node_view import _get_node_view_attribute_serializer, \
    _get_leaf_view_attribute_serializer, \
    _leaf_view_serializer, _get_node_view_serializer, NodeViewContext
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory


class TestNodeViewSerializer(SimpleTestCase):
    def setUp(self):
        self.root_node = NodeGroupYearFactory(node_id=1, code="LBIR100A", title="BIR1BA", year=2018)
        node_parent = NodeGroupYearFactory(node_id=2, code="LTROC250T", title="Tronc commun 2", year=2018)
        node_child = NodeGroupYearFactory(node_id=6, code="LSUBGR150G", title="Sous-groupe 2", year=2018)
        self.link = LinkFactory(parent=node_parent, child=node_child, link_type=link_type.LinkTypes.REFERENCE)

        self.context = NodeViewContext(current_path='1|2|6', root_node=self.root_node, view_path='1|2')
        self.tree = ProgramTreeFactory(root_node=self.root_node)

    def test_serialize_node_ensure_text(self):
        expected_text = self.link.child.code + " - " + self.link.child.title
        serialized_data = _get_node_view_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['text'], expected_text)

    def test_serialize_node_ensure_icon_case_concrete_link(self):
        self.link.link_type = None
        serialized_data = _get_node_view_serializer(self.link, self.tree, self.context)
        self.assertIsNone(serialized_data['icon'])

    def test_serialize_node_ensure_icon_case_reference_link(self):
        self.link.link_type = link_type.LinkTypes.REFERENCE
        serialized_data = _get_node_view_serializer(self.link, self.tree, self.context)
        expected_icon_path = 'img/reference.jpg'
        self.assertIn(expected_icon_path, serialized_data['icon'])


class TestNodeViewAttributeSerializer(SimpleTestCase):
    def setUp(self):
        self.root_node = NodeGroupYearFactory(node_id=1, code="LBIR100A", title="BIR1BA", year=2018)
        self.node_parent = NodeGroupYearFactory(node_id=2, code="LTROC250T", title="Tronc commun 2", year=2018)
        self.node_child = NodeGroupYearFactory(node_id=6, code="LSUBGR150G", title="Sous-groupe 2", year=2018)
        self.link = LinkFactory(parent=self.node_parent, child=self.node_child)

        self.context = NodeViewContext(current_path='1|2|6', root_node=self.root_node, view_path='1|2')
        tree = ProgramTreeFactory(root_node=self.root_node)
        self.serialized_data = _get_node_view_attribute_serializer(self.link, tree, self.context)

    def test_serialize_node_attr_ensure_detach_url(self):
        expected_url = reverse_with_get(
            'tree_detach_node',
            get={"path": self.context.current_path, 'redirect_path': self.context.view_path}
        )
        self.assertEqual(self.serialized_data['detach_url'], expected_url)

    def test_serialize_node_attr_ensure_paste_url(self):
        expected_url = reverse_with_get(
            'tree_paste_node',
            get={"path": self.context.current_path, 'redirect_path': self.context.view_path}
        )
        self.assertEqual(self.serialized_data['paste_url'], expected_url)

    def test_serializer_node_attr_ensure_search_url(self):
        expected_url = reverse_with_get(
            'quick_search_education_group',
            args=[self.root_node.academic_year.year],
            get={"path": self.context.current_path, 'redirect_path': self.context.view_path}
        )
        self.assertEqual(self.serialized_data['search_url'], expected_url)

    def test_serializer_node_attr_ensure_get_title(self):
        expected_title = self.link.child.code
        self.assertEqual(self.serialized_data['title'], expected_title)

    def test_serializer_node_attr_ensure_get_href(self):
        expected_url = reverse_with_get(
            'element_identification',
            args=[self.link.child.year, self.link.child.code],
            get={"path": self.context.current_path}
        )
        self.assertEqual(self.serialized_data['href'], expected_url)

    def test_serializer_node_attr_ensure_element_id(self):
        self.assertEqual(self.serialized_data['element_id'], self.link.child.pk)


class TestLeafViewSerializer(SimpleTestCase):
    def setUp(self):
        self.root_node = NodeGroupYearFactory(node_id=1, code="LBIR100A", title="BIR1BA", year=2018)
        node_parent = NodeGroupYearFactory(node_id=2, code="LTROC250T", title="Tronc commun 2", year=2018)
        leaf_child = NodeLearningUnitYearFactory(node_id=9, code="LSUBGR150G", title="Sous-groupe 2", year=2018)
        self.link = LinkFactory(parent=node_parent, child=leaf_child)

        self.context = NodeViewContext(current_path='1|2|9', root_node=self.root_node, view_path='1|2')
        self.tree = ProgramTreeFactory(root_node=self.root_node)

    def test_serializer_leaf_ensure_text_case_leaf_have_same_year_of_root(self):
        expected_text = self.link.child.code
        serialized_data = _leaf_view_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['text'], expected_text)

    def test_serializer_leaf_ensure_text_case_leaf_doesnt_have_same_year_of_root(self):
        self.link.child.year = self.root_node.year - 1
        expected_text = "|" + str(self.link.child.year) + "|" + self.link.child.code
        serialized_data = _leaf_view_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['text'], expected_text)

    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.has_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=True)
    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.is_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=True)
    def test_serializer_leaf_ensure_get_icon_with_prerequisites_and_is_prerequisite(
            self,
            mock_is_prerequisite,
            mock_has_prerequisite,
    ):
        expected_icon = "fa fa-exchange-alt"
        serialized_data = _leaf_view_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['icon'], expected_icon)

    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.has_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=False)
    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.is_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=True)
    def test_serializer_leaf_ensure_get_icon_no_prerequisite_but_is_prerequisite(
            self,
            mock_is_prerequisite,
            mock_has_prerequisite,
    ):
        expected_icon = "fa fa-arrow-right"
        serialized_data = _leaf_view_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['icon'], expected_icon)

    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.has_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=True)
    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.is_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=False)
    def test_serializer_leaf_ensure_get_icon_with_prerequisites_but_is_not_prerequisite(
            self,
            mock_is_prerequisite,
            mock_has_prerequisite,
    ):
        expected_icon = "fa fa-arrow-left"
        serialized_data = _leaf_view_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['icon'], expected_icon)

    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.has_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=False)
    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.is_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=False)
    def test_serializer_leaf_ensure_get_icon_no_prerequisites_and_is_not_prerequisite(
            self,
            mock_is_prerequisite,
            mock_has_prerequisite,
    ):
        expected_icon = "far fa-file"
        serialized_data = _leaf_view_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['icon'], expected_icon)


class TestLeafViewAttributeSerializer(SimpleTestCase):
    def setUp(self):
        self.root_node = NodeGroupYearFactory(node_id=1, code="LBIR100A", title="BIR1BA", year=2018)
        node_parent = NodeGroupYearFactory(node_id=2, code="LTROC250T", title="Tronc commun 2", year=2018)
        leaf_child = NodeLearningUnitYearFactory(node_id=9, code="LSUBGR150G", title="Sous-groupe 2", year=2018)
        self.link = LinkFactory(parent=node_parent, child=leaf_child)

        self.context = NodeViewContext(current_path='1|2|9', root_node=self.root_node, view_path='1|2')
        self.tree = ProgramTreeFactory(root_node=self.root_node)

    def test_serializer_node_attr_ensure_get_href(self):
        expected_url = reverse_with_get(
            'learning_unit_utilization',
            args=[self.root_node.pk, self.link.child.pk],
            get={"path": self.context.current_path}
        )
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['href'], expected_url)

    def test_serializer_node_attr_ensure_get_element_type(self):
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['element_type'], NodeType.LEARNING_UNIT.name)

    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.has_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=True)
    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.is_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=True)
    def test_serializer_node_attr_ensure_get_title_with_prerequisites_and_is_prerequisite(
            self,
            mock_is_prerequisite,
            mock_has_prerequisite,
    ):
        expected_title = "%s\n%s" % (self.link.child.title,
                                     _("The learning unit has prerequisites and is a prerequisite"))
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['title'], expected_title)

    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.has_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=False)
    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.is_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=True)
    def test_serializer_node_attr_ensure_get_title_no_prerequisite_but_is_prerequisite(
            self,
            mock_is_prerequisite,
            mock_has_prerequisite,
    ):
        expected_title = "%s\n%s" % (self.link.child.title, _("The learning unit is a prerequisite"))
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['title'], expected_title)

    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.has_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=True)
    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.is_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=False)
    def test_serializer_node_attr_ensure_get_title_with_prerequisites_but_is_not_prerequisite(
            self,
            mock_is_prerequisite,
            mock_has_prerequisite,
    ):
        expected_title = "%s\n%s" % (self.link.child.title, _("The learning unit has prerequisites"))
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['title'], expected_title)

    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.has_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=False)
    @mock.patch('program_management.ddd.domain.node.NodeLearningUnitYear.is_prerequisite',
                new_callable=mock.PropertyMock,
                return_value=False)
    def test_serializer_node_attr_ensure_get_title_no_prerequisites_and_is_not_prerequisite(
            self,
            mock_is_prerequisite,
            mock_has_prerequisite,
    ):
        expected_title = self.link.child.title
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['title'], expected_title)

    def test_serializer_node_attr_ensure_get_css_class_proposal_creation(self):
        self.link.child.proposal_type = ProposalType.CREATION.name
        expected_css_class = "proposal proposal_creation"
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['class'], expected_css_class)

    def test_serializer_node_attr_ensure_get_css_class_proposal_modification(self):
        self.link.child.proposal_type = ProposalType.MODIFICATION.name
        expected_css_class = "proposal proposal_modification"
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['class'], expected_css_class)

    def test_serializer_node_attr_ensure_get_css_class_proposal_transformation(self):
        self.link.child.proposal_type = ProposalType.TRANSFORMATION.name
        expected_css_class = "proposal proposal_transformation"
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['class'], expected_css_class)

    def test_serializer_node_attr_ensure_get_css_class_proposal_transformation_modification(self):
        self.link.child.proposal_type = ProposalType.TRANSFORMATION_AND_MODIFICATION.name
        expected_css_class = "proposal proposal_transformation_modification"
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['class'], expected_css_class)

    def test_serializer_node_attr_ensure_get_css_class_proposal_suppression(self):
        self.link.child.proposal_type = ProposalType.SUPPRESSION.name
        expected_css_class = "proposal proposal_suppression"
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['class'], expected_css_class)

    def test_serializer_node_attr_ensure_get_css_class_no_proposal(self):
        self.link.child.proposal_type = None
        expected_css_class = ""
        serialized_data = _get_leaf_view_attribute_serializer(self.link, self.tree, self.context)
        self.assertEqual(serialized_data['class'], expected_css_class)


class TestVersionNodeViewSerializerInEn(SimpleTestCase):
    def setUp(self):
        self.root_node_without_en_title = NodeGroupYearFactory(
            node_id=1, code="LBIR100A", title="BIR1BA", year=2018,
            node_type=random.choice(TrainingType.finality_types_enum())
        )
        self.tree_fr_no_en = ProgramTreeFactory(root_node=self.root_node_without_en_title)
        self.tree_version_fr_no_en = ProgramTreeVersionFactory(tree=self.tree_fr_no_en, entity_id__version_name='CEMS',
                                                               title_fr='Title fr', title_en=None)

        self.root_node_with_fr_en_title = NodeGroupYearFactory(
            node_id=1, code="LCOM100A", title="COM1BA", year=2018,
            node_type=random.choice(TrainingType.finality_types_enum())
        )
        self.tree_fr_en = ProgramTreeFactory(root_node=self.root_node_with_fr_en_title)
        self.tree_version_fr_en = ProgramTreeVersionFactory(tree=self.tree_fr_en, entity_id__version_name='CEMS',
                                                            title_fr='Title fr', title_en='Title en')

        self.root_node_without_fr_title = NodeGroupYearFactory(
            node_id=1, code="LCOB100A", title="COBBA", year=2018,
            node_type=random.choice(TrainingType.finality_types_enum())
        )
        self.tree_without_fr = ProgramTreeFactory(root_node=self.root_node_without_fr_title)
        self.tree_version_without_fr_ = ProgramTreeVersionFactory(tree=self.tree_without_fr,
                                                                  entity_id__version_name='CEMS',
                                                                  title_fr=None)
