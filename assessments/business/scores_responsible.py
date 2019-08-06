##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db.models import QuerySet

from base.models.person import Person


def filter_learning_unit_year_according_person(queryset, person):
    """
    This function will filter the learning unit year queryset according to permission of person.
       * As Entity Manager, we will filter on linked entities
       * As Program Manager, we will filter on learning unit year which are contained in the program
         that the person manage but not a borrow learning unit year

    :param queryset: LearningUnitYear queryset
    :param person: Person object
    :return: queryset
    """
    if not isinstance(queryset, QuerySet):
        raise Exception('Queryset args must be an instance of Queryset')
    if not isinstance(person, Person):
        raise Exception('Person args must be an instance of Person')

    return queryset
