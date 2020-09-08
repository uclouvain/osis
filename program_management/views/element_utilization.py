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
from typing import Dict, List, Any

from django.urls import reverse

from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd import command
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.service.read import search_tree_versions_using_node_service
from program_management.serializers.node_view import get_program_tree_version_name
from program_management.views.generic import LearningUnitGeneric


class LearningUnitUtilization(PermissionRequiredMixin, LearningUnitGeneric):
    template_name = "learning_unit/tab_utilization.html"

    permission_required = 'base.view_educationgroup'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cmd = command.GetProgramTreesVersionFromNodeCommand(code=self.node.code, year=self.node.year)
        program_trees_versions = search_tree_versions_using_node_service.search_tree_versions_using_node(cmd)

        context['utilization_rows'] = self._get_utilization_rows(program_trees_versions)
        return context

    def _get_utilization_rows(self, program_trees_versions):
        utilization_rows = []
        parents = []
        for program_tree_version in program_trees_versions:
            tree = program_tree_version.get_tree()

            for link in tree.get_links_using_node(self.node):
                parent_node_identity = NodeIdentity(code=link.parent.code, year=link.parent.year)
                if parent_node_identity not in parents:
                    parents.append(parent_node_identity)
                    utilization_rows.append(
                        self._build_utilization_row(link, parent_node_identity, program_tree_version,
                                                    program_trees_versions)
                    )
        return sorted(utilization_rows, key=lambda row: row['link'].parent.code)

    def _build_utilization_row(self, link, parent_node_identity, program_tree_version, program_trees_versions):
        return {'link': link,
                'link_parent_version_label': get_program_tree_version_name(
                    parent_node_identity,
                    ProgramTreeVersionRepository.search_all_versions_from_root_node(parent_node_identity)
                ),
                'root_nodes': self._find_trainings_using_link(link.parent, program_trees_versions),
                'root_version_label': "{}".format(
                    program_tree_version.version_label if program_tree_version.version_label else ''
                ),
                }

    @staticmethod
    def _find_trainings_using_link(link: 'Link', program_trees_versions) -> List[Dict[str, Any]]:
        program_trees_versions_using_link = []
        for program_trees_version in program_trees_versions:
            if program_trees_version.get_tree().get_node_by_code_and_year(link.code, link.year):
                program_trees_versions_using_link.append(program_trees_version)

        trainings = []
        for program_tree_version in program_trees_versions_using_link:
            root_node = program_tree_version.get_tree().root_node
            trainings.append({
                'root_node': root_node,
                'root_version_label': program_tree_version.version_label,
                'root_url': reverse('element_identification',
                                    kwargs={'code': root_node.code,
                                            'year': root_node.year})
            })
        return trainings
