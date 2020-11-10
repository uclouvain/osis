############################################################################
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
############################################################################
from django.db.models import F


def convert_order_by_strings_to_expressions(order_by):
    def _convert_field_to_expression(field):
        reverse_order_character = "-"
        expression = F(field.strip(reverse_order_character))
        if field.startswith("-"):
            expression = expression.desc()
        return expression

    return tuple(_convert_field_to_expression(field) for field in order_by)


def dict_fetchall(cursor):  # Inspired from https://docs.djangoproject.com
    """
    Return all rows from a cursor as a dict
    """
    desc = cursor.description
    columns = [col[0] for col in desc]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
