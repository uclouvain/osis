##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.	#    courses, programs and so on.
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
#    GNU General Public License for more details.	#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.	#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import SimpleTestCase

from program_management.ddd.command import CreateProgramTreeVersionCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion, ProgramTreeVersionBuilder, \
    ProgramTreeVersionIdentity


class TestBuildFromStandard(SimpleTestCase):
    def test_should_copy_values_from_standard_if_no_attrs_passed(self):
        builder = ProgramTreeVersionBuilder()
        version_identity = ProgramTreeVersionIdentity(
            offer_acronym='DROI2M',
            year=2020,
            version_name="",
            is_transition=False
        )
        tree_version_standard = ProgramTreeVersion(version_identity)
        command = CreateProgramTreeVersionCommand(
            version_name="TEST", title_en="en", title_fr="fr", is_transition=False, offer_acronym="DROI2M", year=2020
        )

        result = builder.build_from(tree_version_standard, command)
        self.assertEqual(result.entity_id.offer_acronym, tree_version_standard.entity_id.offer_acronym)
        self.assertEqual(result.entity_id.year, tree_version_standard.entity_id.year)
        self.assertEqual(result.entity_id.version_name, "TEST")
        self.assertEqual(result.entity_id.is_transition, False)

        self.assertEqual(result.title_en, "en")
        self.assertEqual(result.title_fr, "fr")
        self.assertIsNone(result.offer)
        self.assertIsNone(result.root_group)
