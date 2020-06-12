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

from django.test import TestCase

from base.tests.factories.education_group_year import EducationGroupYearFactory
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory


class TestVersionRepositoryCreateMethod(TestCase):
    def setUp(self):
        self.offer = EducationGroupYearFactory()
        self.root_group = GroupYearFactory(academic_year=self.offer.academic_year)
        self.repository = ProgramTreeVersionRepository()

    def test_simple_case_creation(self):
        domain_object: ProgramTreeVersion = ProgramTreeVersionFactory(
            entity_identity__offer_acronym=self.offer.acronym,
            entity_identity__year=self.offer.academic_year.year,
            program_tree_identity__code=self.root_group.partial_acronym,
            program_tree_identity__year=self.root_group.academic_year.year,
        )
        self.repository.create(domain_object)

        database_object = EducationGroupVersion.objects.get(
            offer__acronym=domain_object.entity_id.offer_acronym,
            offer__academic_year__year=domain_object.entity_id.year,
            version_name=domain_object.entity_id.version_name,
            is_transition=domain_object.entity_id.is_transition,
        )

        self.assertEqual(database_object.offer_id, self.offer.id)
        self.assertEqual(database_object.root_group_id, self.root_group.id)
        self.assertEqual(database_object.is_transition, domain_object.is_transition)
        self.assertEqual(database_object.version_name, domain_object.version_name)
        self.assertEqual(database_object.title_fr, domain_object.title_fr)
        self.assertEqual(database_object.title_en, domain_object.title_en)
