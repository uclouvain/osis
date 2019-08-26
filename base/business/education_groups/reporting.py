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
import itertools

from django.db.models import QuerySet
from django.utils.translation import gettext as _
from openpyxl import Workbook
from openpyxl.styles import Style, Border, Side, Color, PatternFill, Font
from openpyxl.styles.borders import BORDER_THICK
from openpyxl.styles.colors import RED

from base.models.education_group_year import EducationGroupYear
from base.models.enums.prerequisite_operator import AND, OR
from osis_common.document.xls_build import _build_worksheet, CONTENT_KEY, HEADER_TITLES_KEY, WORKSHEET_TITLE_KEY, \
    STYLED_CELLS, STYLE_NO_GRAY

STYLE_BORDER_BOTTOM = Style(
    border=Border(
        bottom=Side(
            border_style=BORDER_THICK, color=Color('FF000000')
        )
    )
)
STYLE_GRAY = Style(fill=PatternFill(patternType='solid', fgColor=Color('D1D1D1')))
STYLE_LIGHT_GRAY = Style(fill=PatternFill(patternType='solid', fgColor=Color('E1E1E1')))
STYLE_LIGHTER_GRAY = Style(fill=PatternFill(patternType='solid', fgColor=Color('F1F1F1')))


def generate_prerequisites_workbook(egy: EducationGroupYear, prerequisites_qs: QuerySet):
    workbook = Workbook(encoding='utf-8')

    worksheet_data = {
        WORKSHEET_TITLE_KEY: _("Formation prerequisites"),
        HEADER_TITLES_KEY: _build_header(egy),
        CONTENT_KEY: _build_content(prerequisites_qs),
        STYLED_CELLS: _style_cells(prerequisites_qs)
    }

    _build_worksheet(worksheet_data, workbook, 0)

    _merge_cells(prerequisites_qs, workbook)
    _post_style_cell(workbook)

    return workbook


def _build_header(egy: EducationGroupYear):
    return (egy.acronym, egy.title)


def _build_content(prerequisites_qs: QuerySet):
    content = [(_("Official"),)]
    for prerequisite in prerequisites_qs:
        content.append(
            (prerequisite.learning_unit_year.acronym, prerequisite.learning_unit_year.complete_title)
        )
        content.extend(
            _build_item_rows(prerequisite)
        )
    return content


def _build_item_rows(prerequisite):
    content = []
    groups_generator = itertools.groupby(prerequisite.items, key=lambda item: item.group_number)
    for key, group_gen in groups_generator:
        group = list(group_gen)
        if len(group) == 1:
            prerequisite_item = group[0]
            content.append(
                [
                    (_("has as prerequisite") + " :") if prerequisite_item.group_number == 1 else None,
                    _(prerequisite.main_operator) if prerequisite_item.group_number != 1 else None,
                    prerequisite_item.learning_unit.luys[0].acronym,
                    prerequisite_item.learning_unit.luys[0].complete_title
                ]
            )
        else:
            first_item = group[0]
            content.append(
                [
                    (_("has as prerequisite") + ":") if first_item.group_number == 1 else None,
                    _(prerequisite.main_operator) if first_item.group_number != 1 else None,
                    "(" + first_item.learning_unit.luys[0].acronym,
                    first_item.learning_unit.luys[0].complete_title
                ]
            )

            for item in group[1:-1]:
                content.append(
                    [
                        None,
                        _(prerequisite.secondary_operator),
                        item.learning_unit.luys[0].acronym,
                        item.learning_unit.luys[0].complete_title
                    ]
                )

            last_item = group[-1]
            content.append(
                [
                    None,
                    _(prerequisite.secondary_operator),
                    last_item.learning_unit.luys[0].acronym + ")",
                    last_item.learning_unit.luys[0].complete_title
                ]
            )
    return content


def _style_cells(prerequisites_qs: QuerySet):
    luy_acronym_cells = []
    row_index = 3
    for prerequisite in prerequisites_qs:
        luy_acronym_cells.append(
            "A{row_index}".format(row_index=row_index)
        )
        row_index += (len(prerequisite.items) + 1)

    luy_title_cells = []
    row_index = 3
    for prerequisite in prerequisites_qs:
        luy_title_cells.append(
            "B{row_index}".format(row_index=row_index)
        )
        row_index += (len(prerequisite.items) + 1)

    items_cells = []
    row_index = 3
    for prerequisite in prerequisites_qs:
        for i, item in enumerate(prerequisite.items):
            if i % 2 == 0:
                items_cells.append(
                    "C{row_index}".format(row_index=row_index + i + 1)
                )
                items_cells.append(
                    "D{row_index}".format(row_index=row_index + i + 1)
                )
        row_index += len(prerequisite.items) + 1

    return {
        STYLE_NO_GRAY: ["A1", "B1"],
        STYLE_BORDER_BOTTOM: ["A2"],
        STYLE_GRAY: luy_acronym_cells,
        STYLE_LIGHT_GRAY: luy_title_cells,
        STYLE_LIGHTER_GRAY: items_cells
    }


def _merge_cells(prerequisites_qs, workbook):
    worksheet = workbook.worksheets[0]
    row_index = 3
    for prerequisite in prerequisites_qs:
        worksheet.merge_cells(start_row=row_index, end_row=row_index, start_column=2, end_column=4)
        row_index += (len(prerequisite.items) + 1)


def _post_style_cell(workbook: Workbook):
    worksheet = workbook.worksheets[0]

    main_operator = None
    for row_index in range(3, worksheet.max_row + 1):
        cell = worksheet.cell(row=row_index, column=2)

        if not cell.value or cell.value not in (_(AND), _(OR)):
            main_operator = None

        elif main_operator is None:
            main_operator = cell.value

        elif main_operator != cell.value:
            cell.style = Style(
                font=Font(color=RED)
            )
