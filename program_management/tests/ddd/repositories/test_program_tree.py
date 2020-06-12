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

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from education_group.models.group import Group
from education_group.models.group_year import GroupYear
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.models.element import Element
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory


class TestProgramTreeRepositoryCreateMethod(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)

    def setUp(self):
        self.repository = ProgramTreeRepository()

    def test_creates_node_if_not_exists(self):
        domain_object = ProgramTreeFactory(
            root_node__year=self.academic_year.year,
            root_node__start_year=self.academic_year.year,
            root_node__end_date=self.academic_year.year,
        )
        domain_object.root_node._has_changed = True
        EducationGroupTypeFactory(name=domain_object.root_node.node_type.name)

        self.repository.create(domain_object)

        self.assertTrue(
            Group.objects.filter(
                groupyear__partial_acronym=domain_object.entity_id.code,
                groupyear__academic_year__year=domain_object.entity_id.year,
            ).exists()
        )
        self.assertTrue(
            GroupYear.objects.filter(
                partial_acronym=domain_object.entity_id.code,
                academic_year__year=domain_object.entity_id.year,
            ).exists()
        )
        self.assertTrue(
            Element.objects.filter(
                group_year__partial_acronym=domain_object.entity_id.code,
                group_year__academic_year__year=domain_object.entity_id.year,
            ).exists()
        )
