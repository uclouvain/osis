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
from django.forms import model_to_dict
from django.test import TestCase

from base.models.enums import education_group_types
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.education_group_type import MiniTrainingEducationGroupTypeFactory
from base.tests.factories.entity_version import EntityVersionFactory
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._entity import Entity as EntityValueObject
from education_group.ddd.domain.mini_training import MiniTrainingIdentity, MiniTraining
from education_group.ddd.repository import mini_training
from education_group.models import group_year, group
from education_group.tests.factories.mini_training import MiniTrainingFactory
from program_management.models import education_group_version


class TestMiniTrainingRepositoryCreateMethod(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls._create_foreign_key_database_data()
        cls.mini_training = MiniTrainingFactory(
            entity_identity=MiniTrainingIdentity(code="LOIS58", year=cls.academic_year.year),
            start_year=cls.academic_year.year,
            type=education_group_types.MiniTrainingType[cls.education_group_type.name],
            management_entity=EntityValueObject(acronym='DRT'),
            teaching_campus=Campus(
                name=cls.campus.name,
                university_name=cls.campus.organization.name,
            ),
        )

    @classmethod
    def _create_foreign_key_database_data(cls):
        cls.academic_year = AcademicYearFactory()
        cls.management_entity_version = EntityVersionFactory(acronym='DRT')
        cls.education_group_type = MiniTrainingEducationGroupTypeFactory()
        cls.campus = CampusFactory()

    def test_should_create_db_data_with_correct_values_taken_from_domain_object(self):
        mini_training_identity = mini_training.MiniTrainingRepository.create(self.mini_training)

        version = education_group_version.EducationGroupVersion.objects.get(
            root_group__partial_acronym=mini_training_identity.code,
            root_group__academic_year__year=mini_training_identity.year
        )
        group_year_created = group_year.GroupYear.objects.get(
            partial_acronym=mini_training_identity.code,
            academic_year__year=mini_training_identity.year
        )
        self.assert_education_group_version_equal_to_domain(version, self.mini_training)
        self.assert_group_equal_to_domain(group_year_created.group, self.mini_training)
        self.assert_group_year_equal_to_domain(group_year_created, self.mini_training)

    def assert_education_group_version_equal_to_domain(
            self,
            db_version: education_group_version.EducationGroupVersion,
            domain_obj: MiniTraining):
        expected_values = {
            "title_fr": domain_obj.titles.title_fr,
            "title_en": domain_obj.titles.title_en,
            "is_transition": False,
            "version_name": ""
        }
        actual_values = model_to_dict(
            db_version,
            fields=("title_fr", "title_en", "is_transition", "version_name")
        )
        self.assertDictEqual(expected_values, actual_values)

    def assert_group_equal_to_domain(self, db_obj: group.Group, domain_obj: MiniTraining):
        expected_values = {
            "start_year": self.academic_year.id,
            "end_year": domain_obj.end_year
        }
        actual_values = model_to_dict(
            db_obj,
            fields=("start_year", "end_year")
        )
        self.assertDictEqual(expected_values, actual_values)

    def assert_group_year_equal_to_domain(self, db_obj: group_year.GroupYear, domain_obj: MiniTraining):
        expected_values = {
            "academic_year": self.academic_year.id,
            "partial_acronym": domain_obj.code,
            "education_group_type": self.education_group_type.id,
            "acronym": domain_obj.abbreviated_title,
            "title_fr": domain_obj.titles.title_fr,
            "title_en": domain_obj.titles.title_en,
            "credits": domain_obj.credits,
            "constraint_type": domain_obj.content_constraint.type.name,
            "min_constraint": domain_obj.content_constraint.minimum,
            "max_constraint": domain_obj.content_constraint.maximum,
            "management_entity": self.management_entity_version.entity.id,
            "main_teaching_campus": self.campus.id,
        }

        actual_values = model_to_dict(
            db_obj,
            fields=(
                "academic_year", "partial_acronym", "education_group_type", "acronym", "title_fr", "title_en",
                "credits", "constraint_type", "min_constraint", "max_constraint", "management_entity",
                "main_teaching_campus"
            )
        )
        self.assertDictEqual(expected_values, actual_values)



