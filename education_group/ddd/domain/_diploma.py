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
from typing import List

from osis_common.ddd import interface


class DiplomaAim(interface.ValueObject):

    def __init__(self, section: int, code: int, description: str):
        self.section = section
        self.code = code
        self.description = description

    def __eq__(self, other):
        return self.section == other.section \
               and self.code == other.code \
               and self.description == other.description

    def __hash__(self):
        return hash(str(self.section) + str(self.code) + self.description)


# FIXME :: should be an Entity in another Domain, and Training should have just an EntityIdentity to get this object.
class Diploma(interface.ValueObject):
    def __init__(self, leads_to_diploma: bool, printing_title: str, professional_title: str, aims: List['DiplomaAim']):
        self.leads_to_diploma = leads_to_diploma or False
        self.printing_title = printing_title or ''
        self.professional_title = professional_title or ''
        self.aims = aims or []

    def __eq__(self, other):
        return self.leads_to_diploma == other.leads_to_diploma \
               and self.printing_title == other.printing_title \
               and self.professional_title == other.professional_title

    def __hash__(self):
        return hash(str(self.leads_to_diploma) + self.printing_title + self.professional_title)
