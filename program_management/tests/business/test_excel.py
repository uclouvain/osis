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

from django.test import SimpleTestCase
from django.utils.translation import gettext_lazy as _
from django.test.utils import override_settings
from base.models.enums.prerequisite_operator import AND, OR

from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory

from program_management.tests.ddd.factories.prerequisite import PrerequisiteFactory, PrerequisiteItemGroupFactory, PrerequisiteItemFactory
from program_management.tests.ddd.factories.prerequisite import cast_to_prerequisite
from program_management.business.excel import _build_excel_lines
from program_management.business.excel import HeaderLine, OfficialTextLine, LearningUnitYearLine, PrerequisiteItemLine


class TestGeneratePrerequisitesWorkbook(SimpleTestCase):

    def setUp(self):
        self.program_tree = ProgramTreeFactory()
        yr = 2019
        self.link0 = LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="LOSIS1121",
                                              year=yr)
        )
        self.link1 = LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="MARC2547",
                                              year=yr)
        )
        self.link2 = LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="MECK8960",
                                              year=yr)
        )
        self.link3 = LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="BREM5890",
                                              year=yr)
        )
        self.link4 = LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="MARC2548",
                                              year=yr)
        )
        self.link5 = LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="MECK8968",
                                              year=yr)
        )
        link6 = LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="BREM5898",
                                              year=yr)
        )

        self.children = [self.link0.child, self.link1.child, self.link2.child, self.link3.child, self.link4.child, self.link5.child, link6.child]
        self.luy_children = [self.link0.child, self.link1.child, self.link2.child, self.link3.child, self.link4.child, self.link5.child, link6.child]
        node_that_is_prerequisite = self.link1.child
        self.link0.child.set_prerequisite(cast_to_prerequisite(node_that_is_prerequisite))

        item3 = PrerequisiteItemFactory(code=self.link3.child.code, year=self.link3.child.year)
        item4 = PrerequisiteItemFactory(code=self.link4.child.code, year=self.link4.child.year)
        item5 = PrerequisiteItemFactory(code=self.link5.child.code, year=self.link5.child.year)
        prerequisite = PrerequisiteFactory(
            prerequisite_item_groups=[
                PrerequisiteItemGroupFactory(
                    prerequisite_items=[item3]
                ),
                PrerequisiteItemGroupFactory(
                    prerequisite_items=[item4, item5]
                ),
            ]
        )

        self.link2.child.set_prerequisite(prerequisite)

    def test_header_lines(self):
        expected_first_line = HeaderLine(egy_acronym=self.program_tree.root_node.title,
                                         egy_title=self.program_tree.root_node.group_title_en,
                                         code_header=_('Code'),
                                         title_header=_('Title'),
                                         credits_header=_('Cred. rel./abs.'),
                                         block_header=_('Block'),
                                         mandatory_header=_('Mandatory')
                                         )
        expected_second_line = OfficialTextLine(text=_("Official"))

        headers = _build_excel_lines(self.program_tree)
        self.assertEqual(expected_first_line, headers[0])
        self.assertEqual(expected_second_line, headers[1])

    @override_settings(LANGUAGES=[('en', 'English'), ], LANGUAGE_CODE='en')
    def test_when_learning_unit_year_has_one_prerequisite(self):
        content = _build_excel_lines(self.program_tree)
        learning_unit_year_line = content[2]
        prerequisite_item_line = content[3]

        expected_learning_unit_year_line = LearningUnitYearLine(luy_acronym=self.luy_children[0].code,
                                                                luy_title=self.luy_children[0].complete_title)
        expected_prerequisite_item_line = PrerequisiteItemLine(text='{} :'.format(_('has as prerequisite')),
                                                               operator=None,
                                                               luy_acronym=self.luy_children[1].code,
                                                               luy_title=self.luy_children[1].title,
                                                               credits=self.link1.relative_credits_repr,
                                                               block=str(self.link1.block),
                                                               mandatory=_("Yes") if self.link1.is_mandatory else _("No")
                                                               )
        self.assertEqual(expected_learning_unit_year_line, learning_unit_year_line)
        self.assertEqual(expected_prerequisite_item_line, prerequisite_item_line)

    @override_settings(LANGUAGES=[('en', 'English'), ], LANGUAGE_CODE='en')
    def test_when_learning_unit_year_has_multiple_prerequisites(self):
        content = _build_excel_lines(self.program_tree)

        prerequisite_item_line_1 = content[5]
        expected_prerequisite_item_line1 = PrerequisiteItemLine(
            text='{} :'.format(_('has as prerequisite')),
            operator=None,
            luy_acronym=self.luy_children[3].code,
            luy_title=self.luy_children[3].title,
            credits=self.link3.relative_credits_repr,
            block=str(self.link3.block) if self.link3.block else '',
            mandatory=_("Yes") if self.link3.is_mandatory else _("No")
        )
        self.assertEqual(prerequisite_item_line_1, expected_prerequisite_item_line1)

        prerequisite_item_line_2 = content[6]
        expected_prerequisite_item_line2 = PrerequisiteItemLine(
            text=None,
            operator=_(AND),
            luy_acronym="({}".format(self.luy_children[4].code),
            luy_title=self.luy_children[4].title,
            credits=self.link4.relative_credits_repr,
            block=str(self.link4.block) if self.link4.block else '',
            mandatory=_("Yes") if self.link4.is_mandatory else _("No")
        )
        self.assertEqual(prerequisite_item_line_2, expected_prerequisite_item_line2)

        prerequisite_item_line_3 = content[7]
        expected_prerequisite_item_line3 = PrerequisiteItemLine(
            text=None,
            operator=_(OR),
            luy_acronym="{})".format(self.luy_children[5].code),
            luy_title=self.luy_children[5].title,
            credits=self.link5.relative_credits_repr,
            block=str(self.link5.block) if self.link5.block else '',
            mandatory=_("Yes") if self.link5.is_mandatory else _("No")
        )
        self.assertEqual(prerequisite_item_line_3, expected_prerequisite_item_line3)
