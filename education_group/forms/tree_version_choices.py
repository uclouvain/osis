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
from typing import List, Dict

from django import forms
from django.urls import reverse

# from program_management.ddd.business_types import *
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.service.academic_year_search import ExistingAcademicYearSearch
from program_management.ddd.domain.service.element_id_search import ElementIdByYearSearch, PathElementId, Year
from django.utils.translation import gettext_lazy as _

from program_management.ddd.domain.service.identity_search import NodeIdentitySearch
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository

PresentationObject = object  # FIXME :: to move into osis-common/ddd


class ProgramTreeVersionChoiceOption(PresentationObject):
    def __init__(self, tree_version: 'ProgramTreeVersion'):
        # FIXME :: use dependency injection???
        node_identity = NodeIdentitySearch().get_from_program_tree_identity(tree_version.program_tree_identity)
        self.node_href = _get_href(node_identity)
        self.tree_version_identity = tree_version.entity_id
        self.version_name_display = tree_version.version_name or _('Standard')


def _get_href(node_identity: 'NodeIdentity'):
    return reverse('element_identification', args=[node_identity.year, node_identity.code])


def get_tree_versions_choices(
        node_identity: 'NodeIdentity'
) -> List[ProgramTreeVersionChoiceOption]:

    tree_versions = ProgramTreeVersionRepository.search_all_versions_from_root_node(node_identity)

    return [
        ProgramTreeVersionChoiceOption(tree_version=tree_version)
        for tree_version in sorted(tree_versions)
    ]
