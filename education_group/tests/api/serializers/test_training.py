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
from django.db.models import F
from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.models.enums import organization_type, education_group_types
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory, EducationGroupYearBachelorFactory
from base.tests.factories.entity_version import EntityVersionFactory
from education_group.api.serializers.training import TrainingListSerializer, TrainingDetailSerializer
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory, \
    StandardEducationGroupVersionFactory
from reference.tests.factories.domain import DomainFactory


class TrainingListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.entity_version = EntityVersionFactory(
            entity__organization__type=organization_type.MAIN
        )
        cls.training = EducationGroupYearBachelorFactory(
            acronym='BIR1BA',
            partial_acronym='LBIR1000I',
            academic_year=cls.academic_year,
            management_entity=cls.entity_version.entity,
            administration_entity=cls.entity_version.entity,
        )
        cls.version = EducationGroupVersionFactory(offer=cls.training)
        url = reverse('education_group_api_v1:training-list')
        cls.serializer = TrainingListSerializer(cls.version, context={
            'request': RequestFactory().get(url),
            'language': settings.LANGUAGE_CODE_EN
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'title',
            'title_en',
            'url',
            'version_name',
            'acronym',
            'code',
            'education_group_type',
            'education_group_type_text',
            'academic_year',
            'administration_entity',
            'administration_faculty',
            'management_entity',
            'management_faculty',
            'ares_study',
            'ares_graca',
            'ares_ability',
        ]
        self.assertListEqual(list(self.serializer.data), expected_fields)

    def test_ensure_academic_year_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['academic_year'],
            self.academic_year.year
        )

    def test_ensure_education_group_type_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['education_group_type'],
            self.training.education_group_type.name
        )


class TrainingListSerializerForMasterWithFinalityTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.entity_version = EntityVersionFactory(
            entity__organization__type=organization_type.MAIN
        )
        cls.training = TrainingFactory(
            acronym='GERM2MA',
            partial_acronym='LGERM905A',
            academic_year=cls.academic_year,
            education_group_type__name=education_group_types.TrainingType.MASTER_MA_120.name,
            management_entity=cls.entity_version.entity,
            administration_entity=cls.entity_version.entity
        )
        cls.version = EducationGroupVersionFactory(offer=cls.training)
        url = reverse('education_group_api_v1:training-list')
        cls.serializer = TrainingListSerializer(cls.version, context={
            'request': RequestFactory().get(url),
            'language': settings.LANGUAGE_CODE_EN
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'title',
            'title_en',
            'url',
            'version_name',
            'acronym',
            'code',
            'education_group_type',
            'education_group_type_text',
            'academic_year',
            'administration_entity',
            'administration_faculty',
            'management_entity',
            'management_faculty',
            'ares_study',
            'ares_graca',
            'ares_ability',
            'partial_title',
            'partial_title_en',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_academic_year_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['academic_year'],
            self.academic_year.year
        )

    def test_ensure_education_group_type_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['education_group_type'],
            self.training.education_group_type.name
        )


class TrainingDetailSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.entity_version = EntityVersionFactory(
            entity__organization__type=organization_type.MAIN
        )
        cls.training = EducationGroupYearBachelorFactory(
            acronym='BIR1BA',
            partial_acronym='LBIR1000I',
            academic_year=cls.academic_year,
            management_entity=cls.entity_version.entity,
            administration_entity=cls.entity_version.entity,
            main_domain=DomainFactory(parent=DomainFactory())
        )
        cls.version = StandardEducationGroupVersionFactory(offer=cls.training)
        annotated_version = EducationGroupVersion.objects.annotate(
            domain_code=F('offer__main_domain__code'),
            domain_name=F('offer__main_domain__parent__name'),
        ).get(id=cls.version.id)
        url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': cls.training.acronym,
            'year': cls.academic_year.year
        })
        cls.serializer = TrainingDetailSerializer(annotated_version, context={
            'request': RequestFactory().get(url),
            'language': settings.LANGUAGE_CODE_EN
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'title',
            'title_en',
            'url',
            'version_name',
            'acronym',
            'code',
            'education_group_type',
            'education_group_type_text',
            'academic_year',
            'administration_entity',
            'administration_faculty',
            'management_entity',
            'management_faculty',
            'ares_study',
            'ares_graca',
            'ares_ability',
            'partial_deliberation',
            'admission_exam',
            'funding',
            'funding_direction',
            'funding_cud',
            'funding_direction_cud',
            'academic_type',
            'academic_type_text',
            'university_certificate',
            'dissertation',
            'internship',
            'internship_text',
            'schedule_type',
            'schedule_type_text',
            'english_activities',
            'english_activities_text',
            'other_language_activities',
            'other_language_activities_text',
            'other_campus_activities',
            'other_campus_activities_text',
            'professional_title',
            'joint_diploma',
            'diploma_printing_orientation',
            'diploma_printing_orientation_text',
            'diploma_printing_title',
            'inter_organization_information',
            'inter_university_french_community',
            'inter_university_belgium',
            'inter_university_abroad',
            'primary_language',
            'keywords',
            'duration',
            'duration_unit',
            'duration_unit_text',
            'language_association_text',
            'enrollment_enabled',
            'credits',
            'remark',
            'remark_en',
            'min_constraint',
            'max_constraint',
            'constraint_type',
            'constraint_type_text',
            'weighting',
            'default_learning_unit_enrollment',
            'decree_category',
            'decree_category_text',
            'rate_code',
            'rate_code_text',
            'internal_comment',
            'co_graduation',
            'co_graduation_coefficient',
            'web_re_registration',
            'active',
            'active_text',
            'enrollment_campus',
            'main_teaching_campus',
            'domain_code',
            'domain_name',
            'versions'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_academic_year_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['academic_year'],
            self.academic_year.year
        )

    def test_ensure_education_group_type_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['education_group_type'],
            self.training.education_group_type.name
        )


class TrainingDetailSerializerForMasterWithFinalityTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.entity_version = EntityVersionFactory(
            entity__organization__type=organization_type.MAIN
        )
        cls.training = TrainingFactory(
            acronym='GERM2MA',
            partial_acronym='LGERM905A',
            academic_year=cls.academic_year,
            education_group_type__name=education_group_types.TrainingType.MASTER_MA_120.name,
            management_entity=cls.entity_version.entity,
            administration_entity=cls.entity_version.entity,
            main_domain=DomainFactory(parent=DomainFactory())
        )
        cls.version = StandardEducationGroupVersionFactory(offer=cls.training)
        annotated_version = EducationGroupVersion.objects.annotate(
            domain_code=F('offer__main_domain__code'),
            domain_name=F('offer__main_domain__parent__name'),
        ).get(id=cls.version.id)
        url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': cls.training.acronym,
            'year': cls.academic_year.year
        })
        cls.serializer = TrainingDetailSerializer(annotated_version, context={
            'request': RequestFactory().get(url),
            'language': settings.LANGUAGE_CODE_EN
        })

    def test_contains_expected_fields(self):
        expected_fields = [
            'title',
            'title_en',
            'url',
            'version_name',
            'acronym',
            'code',
            'education_group_type',
            'education_group_type_text',
            'academic_year',
            'administration_entity',
            'administration_faculty',
            'management_entity',
            'management_faculty',
            'ares_study',
            'ares_graca',
            'ares_ability',
            'partial_title',
            'partial_title_en',
            'partial_deliberation',
            'admission_exam',
            'funding',
            'funding_direction',
            'funding_cud',
            'funding_direction_cud',
            'academic_type',
            'academic_type_text',
            'university_certificate',
            'dissertation',
            'internship',
            'internship_text',
            'schedule_type',
            'schedule_type_text',
            'english_activities',
            'english_activities_text',
            'other_language_activities',
            'other_language_activities_text',
            'other_campus_activities',
            'other_campus_activities_text',
            'professional_title',
            'joint_diploma',
            'diploma_printing_orientation',
            'diploma_printing_orientation_text',
            'diploma_printing_title',
            'inter_organization_information',
            'inter_university_french_community',
            'inter_university_belgium',
            'inter_university_abroad',
            'primary_language',
            'keywords',
            'duration',
            'duration_unit',
            'duration_unit_text',
            'language_association_text',
            'enrollment_enabled',
            'credits',
            'remark',
            'remark_en',
            'min_constraint',
            'max_constraint',
            'constraint_type',
            'constraint_type_text',
            'weighting',
            'default_learning_unit_enrollment',
            'decree_category',
            'decree_category_text',
            'rate_code',
            'rate_code_text',
            'internal_comment',
            'co_graduation',
            'co_graduation_coefficient',
            'web_re_registration',
            'active',
            'active_text',
            'enrollment_campus',
            'main_teaching_campus',
            'domain_code',
            'domain_name',
            'versions'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_academic_year_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['academic_year'],
            self.academic_year.year
        )

    def test_ensure_education_group_type_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['education_group_type'],
            self.training.education_group_type.name
        )


class TrainingVersionDetailSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.entity_version = EntityVersionFactory(entity__organization__type=organization_type.MAIN)
        cls.training = TrainingFactory(
            academic_year=cls.academic_year,
            management_entity=cls.entity_version.entity,
            administration_entity=cls.entity_version.entity,
            main_domain=DomainFactory(parent=DomainFactory())
        )
        cls.version = EducationGroupVersionFactory(offer=cls.training, version_name='TEST')
        annotated_version = EducationGroupVersion.objects.annotate(
            domain_code=F('offer__main_domain__code'),
            domain_name=F('offer__main_domain__parent__name'),
        ).get(id=cls.version.id)
        url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': cls.training.acronym,
            'year': cls.academic_year.year,
            'version_name': cls.version.version_name
        })
        cls.serializer = TrainingDetailSerializer(annotated_version, context={
            'request': RequestFactory().get(url),
            'language': settings.LANGUAGE_CODE_EN
        })

    def test_contains_not_field_versions(self):
        self.assertNotIn('versions', list(self.serializer.data.keys()))
