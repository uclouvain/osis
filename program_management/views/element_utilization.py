##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.repositories.find_roots import find_roots
from program_management.ddd.service import tree_service
from program_management.views.generic import LearningUnitGeneric


class LearningUnitUtilization(PermissionRequiredMixin, LearningUnitGeneric):
    template_name = "learning_unit/tab_utilization.html"

    permission_required = 'base.view_educationgroup'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        trees = tree_service.search_trees_using_node(self.node)

        context['utilization_rows'] = []
        for tree in trees:
            context['utilization_rows'] += [link for link in tree.get_links_using_node(self.node)]

        # TODO: Use DDD instead of queryset
        # context["group_element_years"] = self.object.child_leaf.select_related("parent")
        # context["formations"] = find_roots(
        #     list(grp.parent for grp in self.object.child_leaf.select_related("parent")),
        #     as_instances=True
        # )
        return context
