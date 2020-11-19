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

from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.ddd.domain.exception import ParentAndChildMustHaveSameAcademicYearException


class ParentChildSameAcademicYearValidator(business_validator.BusinessValidator):

    def __init__(self, parent_node: 'Node', node_to_add: 'Node'):
        super(ParentChildSameAcademicYearValidator, self).__init__()
        self.node_to_add = node_to_add
        self.parent_node = parent_node

    def validate(self):
        if not self.node_to_add.is_learning_unit() and self.parent_node.year != self.node_to_add.year:
            raise ParentAndChildMustHaveSameAcademicYearException(self.parent_node, self.node_to_add)
