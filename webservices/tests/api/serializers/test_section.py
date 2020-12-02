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
from django.conf import settings
from django.test import TestCase

from base.models.admission_condition import AdmissionCondition
from base.models.enums.education_group_types import TrainingType
from base.tests.factories.admission_condition import AdmissionConditionFactory
from base.tests.factories.education_group_publication_contact import EducationGroupPublicationContactFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory, \
    EducationGroupYearCommonMasterFactory, \
    TrainingFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.translated_text import TranslatedTextFactory
from program_management.ddd.domain.node import NodeGroupYear
from program_management.tests.ddd.factories.node import NodeGroupYearFactory
from webservices.api.serializers.section import SectionSerializer, AchievementSectionSerializer, \
    AdmissionConditionSectionSerializer, ContactsSectionSerializer
from webservices.business import SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA


class SectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'label': 'LABEL',
            'translated_label': 'TRANSLATED_LABEL',
            'text': 'TEXT',
            'dummy': 'DUMMY'
        }
        cls.serializer = SectionSerializer(cls.data_to_serialize)

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'label',
            'content'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_contains_expected_fields_with_free_text(self):
        self.data_to_serialize['free_text'] = 'FREE_TEXT'
        serializer = SectionSerializer(self.data_to_serialize)
        expected_fields = [
            'id',
            'label',
            'content',
        ]
        self.assertListEqual(list(serializer.data.keys()), expected_fields)


class AchievementSectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'id': 'ID',
            'dummy': 'DUMMY'
        }
        cls.language = settings.LANGUAGE_CODE_EN
        cls.egy = EducationGroupYearFactory()
        cls.node = NodeGroupYearFactory(
            node_id=cls.egy.id,
            node_type=cls.egy.education_group_type,
        )
        for label in [SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA]:
            TranslatedTextFactory(
                text_label__label=label,
                reference=cls.egy.id,
                entity=OFFER_YEAR,
                language=cls.language
            )
        cls.serializer = AchievementSectionSerializer(cls.data_to_serialize, context={
            'egy': cls.node,
            'language': cls.language
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'label',
            'content'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class AdmissionConditionSectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'id': 'ID',
            'dummy': 'DUMMY'
        }
        cls.language = settings.LANGUAGE_CODE_EN
        cls.egy = EducationGroupYearFactory(
            acronym='ARKE2M',
            education_group_type__name=TrainingType.PGRM_MASTER_120.name
        )
        cls.node = NodeGroupYearFactory(
            node_type=cls.egy.education_group_type,
            code=cls.egy.partial_acronym,
            year=cls.egy.academic_year.year
        )
        common_egy = EducationGroupYearCommonMasterFactory(academic_year=cls.egy.academic_year)
        AdmissionConditionFactory(education_group_year=common_egy)
        AdmissionConditionFactory(education_group_year=cls.egy)
        cls.serializer = AdmissionConditionSectionSerializer(cls.data_to_serialize, context={
            'root_node': cls.node,
            'language': cls.language,
            'offer': cls.egy
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'label',
            'content'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_get_education_group_year(self):
        self.assertIsInstance(self.serializer.context.get('root_node'), NodeGroupYear)
        self.assertEqual(self.serializer.context.get('root_node'), self.node)

    def test_ensure_admission_condition_is_created_if_not_exists(self):
        training_wihtout_admission_condition = TrainingFactory(education_group_type__name=TrainingType.BACHELOR.name)
        node = NodeGroupYearFactory(
            code=training_wihtout_admission_condition.partial_acronym,
            year=training_wihtout_admission_condition.academic_year.year,
            node_type=training_wihtout_admission_condition.education_group_type,
        )
        serializer = AdmissionConditionSectionSerializer({}, context={
            'root_node': node,
            'language': self.language,
            'offer': training_wihtout_admission_condition
        })

        new_instance = serializer.get_admission_condition()
        self.assertIsInstance(new_instance, AdmissionCondition)
        self.assertEqual(new_instance.education_group_year_id, training_wihtout_admission_condition.pk)


class ContactsSectionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_to_serialize = {
            'id': 'ID',
            'dummy': 'DUMMY'
        }
        cls.language = 'en'
        management_entity = EntityFactory()
        publication_contact_entity = EntityFactory()
        cls.egy = EducationGroupYearFactory(
            management_entity=management_entity,
            publication_contact_entity=publication_contact_entity
        )
        cls.node = NodeGroupYearFactory(
            node_id=cls.egy.id,
            node_type=cls.egy.education_group_type,
        )
        EntityVersionFactory(entity=management_entity)
        EntityVersionFactory(entity=publication_contact_entity)
        EducationGroupPublicationContactFactory(education_group_year=cls.egy)
        cls.serializer = ContactsSectionSerializer(cls.data_to_serialize, context={
            'egy': cls.node,
            'language': cls.language
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'label',
            'content'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
