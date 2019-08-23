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
from openpyxl import Workbook

from base.models.education_group_year import EducationGroupYear


def generate_prerequisites_workbook(egy: EducationGroupYear, prerequisites_qs: iter):
    workbook = Workbook(encoding='utf-8')

    sheet = workbook.active

    # Header
    sheet.append(
        (egy.acronym, egy.title)
    )
    sheet.append(
        ("Officiel",)
    )

    # Content
    for prerequisite in prerequisites_qs:
        sheet.append(
            (prerequisite.learning_unit_year.acronym, prerequisite.learning_unit_year.complete_title)
        )
        for prerequisite_item in prerequisite.items:
            text = "{acronym} {title}".format(
                acronym=prerequisite_item.learning_unit.luys[0].acronym,
                title=prerequisite_item.learning_unit.luys[0].complete_title
            )
            sheet.append(
                ["a comme prérequis :", text]
            )

    return workbook
