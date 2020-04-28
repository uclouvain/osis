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

# TODO : Ici il y a encore peut d'élément pour une attribution...mais après cela devrait servir ne serait-ce pas
# plus intéressant d'avoir un object ddd représentant une personne
# et que cet objet soit exploité par la class Attribution


class Attribution:

    def __init__(
            self,
            teacher_last_name: str = None,
            teacher_first_name: str = None,
            teacher_middle_name: str = None,
            teacher_email: str = None, # TODO : il n'y a pas de type spécifique pour les emails?
    ):
        self.teacher_last_name = teacher_last_name
        self.teacher_first_name = teacher_first_name
        self.teacher_middle_name = teacher_middle_name
        self.teacher_email = teacher_email

    @property
    def teacher_full_name(self):
        return "".join([
            (self.teacher_last_name or "").upper(),
            self.teacher_first_name or "",
            self.teacher_middle_name or ""
        ]).strip()
