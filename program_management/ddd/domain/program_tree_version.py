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

from base.models.authorized_relationship import AuthorizedRelationshipList
from program_management.ddd.business_types import *

STANDARD = ""


class ProgramTreeVersion(ProgramTree):

    def __init__(
            self,
            root_node: 'Node',
            version_name: str = STANDARD,
            is_transition: bool = False,
            title_fr: str = None,
            title_en: str = None,
            authorized_relationships: AuthorizedRelationshipList = None
    ):
        super(ProgramTreeVersion, self).__init__(root_node, authorized_relationships=authorized_relationships)
        self.is_transition = is_transition
        self.version_name = version_name
        self.title_fr = title_fr
        self.title_en = title_en
