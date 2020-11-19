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


class Teacher:

    def __init__(
            self,
            last_name: str = None,
            first_name: str = None,
            middle_name: str = None,
            email: str = None,
    ):
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.email = email

    def __eq__(self, other):
        return self.last_name == other.last_name and \
               self.first_name == other.first_name and \
               self.middle_name == other.middle_name

    def __hash__(self):
        return hash(self.last_name + self.first_name + self.middle_name)

    @property
    def full_name(self):
        return "".join([
            (self.last_name or "").upper(),
            self.first_name or "",
            self.middle_name or ""
        ]).strip()
