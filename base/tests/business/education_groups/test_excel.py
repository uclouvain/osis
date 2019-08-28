##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db.models import Prefetch
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from base.business.education_groups.excel import generate_prerequisites_workbook
from base.models.enums.prerequisite_operator import AND, OR
from base.models.learning_unit_year import LearningUnitYear
from base.models.prerequisite import Prerequisite
from base.models.prerequisite_item import PrerequisiteItem
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearChildLeafFactory
from base.tests.factories.prerequisite import PrerequisiteFactory


class TestGeneratePrerequisitesWorkbook(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()
        cls.child_leaves = GroupElementYearChildLeafFactory.create_batch(
            6,
            parent=cls.education_group_year
        )
        cls.luy_children = [child.child_leaf for child in cls.child_leaves]

        PrerequisiteFactory(
            learning_unit_year=cls.luy_children[0],
            education_group_year=cls.education_group_year,
            items__groups=(
                (cls.luy_children[1],),
            )
        )
        PrerequisiteFactory(
            learning_unit_year=cls.luy_children[2],
            education_group_year=cls.education_group_year,
            items__groups=(
                (cls.luy_children[3],),
                (cls.luy_children[4], cls.luy_children[5])
            )
        )

        cls.prerequisites = Prerequisite.objects.filter(
            education_group_year=cls.education_group_year
        ).prefetch_related(
            Prefetch(
                "prerequisiteitem_set",
                queryset=PrerequisiteItem.objects.order_by(
                    'group_number',
                    'position'
                ).select_related(
                    "learning_unit"
                ).prefetch_related(
                    Prefetch(
                        "learning_unit__learningunityear_set",
                        queryset=LearningUnitYear.objects.filter(academic_year=cls.education_group_year.academic_year),
                        to_attr="luys"
                    )
                ),
                to_attr="items"
            )
        ).select_related(
            "learning_unit_year"
        ).order_by(
            "learning_unit_year__id"
        )

        cls.workbook = generate_prerequisites_workbook(cls.education_group_year, cls.prerequisites)
        cls.sheet = cls.workbook.worksheets[0]

    def test_header_lines(self):
        expected_headers = [
            [self.education_group_year.acronym, self.education_group_year.title],
            [_("Official"), None]
        ]

        headers = [row_to_value(row) for row in self.sheet.iter_rows(range_string="A1:B2")]
        self.assertListEqual(headers, expected_headers)

    def test_when_learning_unit_year_has_one_prerequisite(self):
        expected_content = [
            [self.luy_children[0].acronym, self.luy_children[0].complete_title, None, None],
            [_("has as prerequisite") + " :", '', self.luy_children[1].acronym,
             self.luy_children[1].complete_title_i18n]
        ]

        content = [row_to_value(row) for row in self.sheet.iter_rows(range_string="A3:D4")]
        self.assertListEqual(expected_content, content)

    def test_when_learning_unit_year_has_multiple_prerequisites(self):
        expected_content = [
            [self.luy_children[2].acronym, self.luy_children[2].complete_title, None, None],
            [_("has as prerequisite") + " :", '', self.luy_children[3].acronym,
             self.luy_children[3].complete_title_i18n],
            ['', _(AND), "(" + self.luy_children[4].acronym, self.luy_children[4].complete_title_i18n],
            ['', _(OR), self.luy_children[5].acronym + ")", self.luy_children[5].complete_title_i18n]
        ]
        content = [row_to_value(row) for row in self.sheet.iter_rows(range_string="A5:D8")]
        self.assertListEqual(expected_content, content)


def row_to_value(sheet_row):
    return [cell.value for cell in sheet_row]
