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
from django.utils.translation import gettext_lazy as _

from base.models.enums.prerequisite_operator import AND, OR
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearChildLeafFactory
from base.tests.factories.prerequisite import PrerequisiteFactory
from program_management.business.excel import EducationGroupYearLearningUnitsPrerequisitesToExcel
from program_management.tests.factories.element import ElementGroupYearFactory, ElementLearningUnitYearFactory
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from education_group.tests.factories.group_year import GroupYearFactory as GroupYearFactoryModel


class TestGeneratePrerequisitesWorkbook(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()
        academic_year = cls.education_group_year.academic_year
        cls.grp_yr = GroupYearFactoryModel(academic_year=academic_year)
        cls.element_root = ElementGroupYearFactory(group_year=cls.grp_yr)
        cls.root = cls.element_root.group_year
        cls.education_group_version = EducationGroupVersionFactory(offer=cls.education_group_year,
                                                                   root_group=cls.element_root.group_year)
        ElementLearningUnitYearFactory()

        cls.child_leaves = []
        for i in range(1, 7):
            cls.child_leaves.append(GroupElementYearChildLeafFactory(
                child_element=ElementLearningUnitYearFactory(learning_unit_year__academic_year=academic_year,
                                                             learning_unit_year__acronym="LFAC100{}".format(i)),
                parent_element=cls.element_root)
            )

        luy_acronyms = ["LCORS124" + str(i) for i in range(0, len(cls.child_leaves))]
        for node, acronym in zip(cls.child_leaves, luy_acronyms):
            node.child_element.acronym = acronym
            node.child_element.save()

        cls.luy_children = [child.child_element.learning_unit_year for child in cls.child_leaves]

        PrerequisiteFactory(
            learning_unit_year=cls.luy_children[0],
            education_group_year=cls.education_group_year,
            items__groups=(
                (cls.luy_children[1],),
            ),
            education_group_version=cls.education_group_version
        )

        PrerequisiteFactory(
            learning_unit_year=cls.luy_children[2],
            education_group_year=cls.education_group_year,
            items__groups=(
                (cls.luy_children[3],),
                (cls.luy_children[4], cls.luy_children[5])
            ),
            education_group_version=cls.education_group_version
        )

    def test_header_lines(self):
        # tree.root_node.code,
        # egy_title = tree.root_node.title,
        expected_headers = [
            [self.grp_yr.acronym, self.grp_yr.title_fr, _('Code'), _('Title'),
             _('Cred. rel./abs.'), _('Block'), _('Mandatory')],
            [_("Official"), None, None, None, None, None, None]
        ]

        workbook_prerequisites = \
            EducationGroupYearLearningUnitsPrerequisitesToExcel(self.root.academic_year.year,
                                                                self.root.partial_acronym)._to_workbook()
        sheet_prerequisites = workbook_prerequisites.worksheets[0]

        headers = [row_to_value(row) for row in sheet_prerequisites.iter_rows(range_string="A1:G2")]

        self.assertListEqual(headers, expected_headers)

    def test_when_learning_unit_year_has_one_prerequisite(self):
        # ici
        expected_content = [
            [self.luy_children[0].acronym, self.luy_children[0].complete_title, None, None, None, None, None],

            [_("has as prerequisite") + " :", '',
             self.luy_children[1].acronym,
             self.luy_children[1].complete_title_i18n,
             "{} / {}".format(self.child_leaves[1].relative_credits, self.luy_children[1].credits),
             str(self.child_leaves[1].block) if self.child_leaves[1].block else '',
             _("Yes") if self.child_leaves[1].is_mandatory else _("No")]
        ]
        workbook_prerequisites = \
            EducationGroupYearLearningUnitsPrerequisitesToExcel(self.root.academic_year.year,
                                                                self.root.partial_acronym)._to_workbook()
        sheet_prerequisites = workbook_prerequisites.worksheets[0]
        content = [row_to_value(row) for row in sheet_prerequisites.iter_rows(range_string="A3:G4")]

        self.assertListEqual(expected_content, content)

    def test_when_learning_unit_year_has_multiple_prerequisites(self):
        expected_content = [
            [self.luy_children[2].acronym, self.luy_children[2].complete_title, None, None, None, None, None],

            [_("has as prerequisite") + " :", '', self.luy_children[3].acronym,
             self.luy_children[3].complete_title_i18n,
             "{} / {}".format(self.child_leaves[3].relative_credits, self.luy_children[3].credits),
             str(self.child_leaves[3].block) if self.child_leaves[3].block else '',
             _("Yes") if self.child_leaves[3].is_mandatory else _("No")],

            ['', _(AND), "(" + self.luy_children[4].acronym, self.luy_children[4].complete_title_i18n,
             "{} / {}".format(self.child_leaves[4].relative_credits, self.luy_children[4].credits),
             str(self.child_leaves[4].block) if self.child_leaves[4].block else '',
             _("Yes") if self.child_leaves[4].is_mandatory else _("No")
             ],

            ['', _(OR), self.luy_children[5].acronym + ")", self.luy_children[5].complete_title_i18n,
             "{} / {}".format(self.child_leaves[5].relative_credits, self.luy_children[5].credits),
             str(self.child_leaves[5].block) if self.child_leaves[5].block else '',
             _("Yes") if self.child_leaves[5].is_mandatory else _("No")
             ]
        ]
        workbook_prerequisites = \
            EducationGroupYearLearningUnitsPrerequisitesToExcel(self.root.academic_year.year,
                                                                self.root.partial_acronym)._to_workbook()
        sheet_prerequisites = workbook_prerequisites.worksheets[0]
        content = [row_to_value(row) for row in sheet_prerequisites.iter_rows(range_string="A5:G8")]
        self.assertListEqual(expected_content, content)


def row_to_value(sheet_row):
    return [cell.value for cell in sheet_row]
