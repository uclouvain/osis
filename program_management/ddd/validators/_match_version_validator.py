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
from django.utils.translation import gettext as _

import osis_common.ddd.interface
from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.models.education_group_version import EducationGroupVersion


class MatchVersionValidator(business_validator.BusinessValidator):

    def __init__(self, tree: 'ProgramTree', node_to_add: 'Node'):
        super(MatchVersionValidator, self).__init__()
        self.tree = tree
        self.node_to_add = node_to_add

    def validate(self):
        academic_year = self.node_to_add.academic_year
        root_node_version = EducationGroupVersion.objects.get(
            root_group__partial_acronym=self.tree.root_node.code, root_group__academic_year__year=academic_year.year
        )
        node_to_add_version = EducationGroupVersion.objects.get(
            root_group__partial_acronym=self.node_to_add.code, root_group__academic_year__year=academic_year.year
        )
        if root_node_version.version_name != node_to_add_version.version_name:
            error_msg = _('The child version must be the same as the root node version')
            raise osis_common.ddd.interface.BusinessExceptions([error_msg])
