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
from django.test import TestCase

from program_management.ddd.domain import program_tree_version, exception
from program_management.ddd.repositories import program_tree_version as program_tree_version_repository
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory


class TestProgramTreeVersionDelete(TestCase):
    def test_should_raise_exception_when_no_matching_program_version_found(self):
        program_tree_version_identity = program_tree_version.ProgramTreeVersionIdentity(
            offer_acronym='Acronym',
            year=2018,
            version_name='',
            is_transition=False
        )

        with self.assertRaises(exception.ProgramTreeVersionNotFoundException):
            program_tree_version_repository.ProgramTreeVersionRepository.delete(program_tree_version_identity)

    def test_should_delete_education_group_version_when_matching_program_version_found(self):
        version_db_obj = EducationGroupVersionFactory()
        program_tree_version_identity = program_tree_version.ProgramTreeVersionIdentity(
            offer_acronym=version_db_obj.offer.acronym,
            year=version_db_obj.offer.academic_year.year,
            version_name=version_db_obj.version_name,
            is_transition=version_db_obj.is_transition
        )

        program_tree_version_repository.ProgramTreeVersionRepository.delete(program_tree_version_identity)

        with self.assertRaises(EducationGroupVersion.DoesNotExist):
            EducationGroupVersion.objects.get(pk=version_db_obj.pk)
