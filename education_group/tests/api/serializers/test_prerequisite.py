from django.conf import settings
from django.test import SimpleTestCase, RequestFactory, override_settings
from rest_framework.reverse import reverse

from base.models.enums import prerequisite_operator
from education_group.api.serializers.prerequisite import EducationGroupPrerequisitesSerializerLearningUnit, \
    LearningUnitBaseSerializer
from program_management.ddd.domain import prerequisite
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory


@override_settings(LANGUAGES=[('en', 'English'), ], LANGUAGE_CODE='en')
class TestEducationGroupPrerequisitesSerializer(SimpleTestCase):
    def setUp(self):
        """
        root_node
        |-----common_core
             |---- LDROI100A (UE)
        :return:
        """
        self.root_node = NodeGroupYearFactory(node_id=1, code="LBIR100B", title="Bachelier en droit", year=2018)
        self.common_core = NodeGroupYearFactory(node_id=2, code="LGROUP100A", title="Tronc commun", year=2018)
        self.ldroi100a = NodeLearningUnitYearFactory(node_id=3, code="LDROI100A", title="Introduction", year=2018)

        self.ldroi1300 = NodeLearningUnitYearFactory(node_id=7, code="LDROI1300", title="Introduction droit", year=2018)
        self.lagro2400 = NodeLearningUnitYearFactory(node_id=8, code="LAGRO2400", title="Séminaire agro", year=2018)

        LinkFactory(parent=self.root_node, child=self.common_core)
        LinkFactory(parent=self.common_core, child=self.ldroi100a)

        self.p_group = prerequisite.PrerequisiteItemGroup(operator=prerequisite_operator.AND)
        self.p_group.add_prerequisite_item('LDROI1300', 2018)
        self.p_group2 = prerequisite.PrerequisiteItemGroup(operator=prerequisite_operator.AND)
        self.p_group2.add_prerequisite_item('LAGRO2400', 2018)

        p_req = prerequisite.Prerequisite(main_operator=prerequisite_operator.AND)
        p_req.add_prerequisite_item_group(self.p_group)
        p_req.add_prerequisite_item_group(self.p_group2)
        self.ldroi100a.set_prerequisite(p_req)

        self.tree = ProgramTree(root_node=self.root_node)

        url = reverse('education_group_api_v1:training-prerequisites', kwargs={'year': self.root_node.year,
                                                                               'acronym': self.root_node.code})
        self.request = RequestFactory().get(url)
        self.serializer = EducationGroupPrerequisitesSerializerLearningUnit(self.ldroi100a, context={
            'request': self.request,
            'language': settings.LANGUAGE_CODE_EN,
            'tree': self.tree
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'title',
            'url',
            'code',
            'prerequisites_string',
            'prerequisites',
        ]
        self.assertListEqual(expected_fields, list(self.serializer.data.keys()))

    def test_read_prerequisite_on_training(self):
        with self.subTest('title'):
            self.assertEqual(self.ldroi100a.common_title_en, self.serializer.data.get('title'))

        with self.subTest('url'):
            url = reverse('learning_unit_api_v1:learningunits_read',
                          kwargs={'year': self.ldroi100a.year, 'acronym': self.ldroi100a.code},
                          request=self.request)
            self.assertEqual(url, self.serializer.data.get('url'))

        with self.subTest('code'):
            self.assertEqual(self.ldroi100a.code, self.serializer.data.get('code'))

        with self.subTest('prerequisites_string'):
            self.assertEqual(str(self.ldroi100a.prerequisite), self.serializer.data.get('prerequisites_string'))


class TestLearningUnitBaseSerializer(SimpleTestCase):
    def setUp(self):
        self.ldroi1300 = NodeLearningUnitYearFactory(node_id=7, code="LDROI1300", title="Introduction droit", year=2018)

        url = reverse('education_group_api_v1:training-prerequisites', kwargs={'year': 2018, 'acronym': 'LDROI1300'})
        self.request = RequestFactory().get(url)
        self.serializer = LearningUnitBaseSerializer(self.ldroi1300, context={
            'request': self.request,
            'language': settings.LANGUAGE_CODE_EN,
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'title',
            'url',
            'code',
        ]
        self.assertListEqual(expected_fields, list(self.serializer.data.keys()))

    def test_read(self):
        with self.subTest('title'):
            self.assertEqual(self.ldroi1300.common_title_en, self.serializer.data.get('title'))

        with self.subTest('url'):
            url = reverse('learning_unit_api_v1:learningunits_read',
                          kwargs={'year': self.ldroi1300.year, 'acronym': self.ldroi1300.code},
                          request=self.request)
            self.assertEqual(url, self.serializer.data.get('url'))

        with self.subTest('code'):
            self.assertEqual(self.ldroi1300.code, self.serializer.data.get('code'))
