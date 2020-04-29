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
import json

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import TrainingType, MiniTrainingType, GroupType
from base.models.group_element_year import GroupElementYear
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views.education_groups import perms
from base.views.education_groups.detail import CatalogGenericDetailView
from base.views.mixins import RulesRequiredMixin, FlagMixin, AjaxTemplateMixin
from education_group.models.group_year import GroupYear
from osis_common.utils.models import get_object_or_none
from program_management.ddd.repositories import load_tree
from program_management.models.enums.node_type import NodeType
from program_management.serializers import program_tree_view

NO_PREREQUISITES = TrainingType.finality_types() + [
    MiniTrainingType.OPTION.name,
    MiniTrainingType.MOBILITY_PARTNERSHIP.name,
] + GroupType.get_names()


@method_decorator(login_required, name='dispatch')
class GenericGroupElementYearMixin(FlagMixin, RulesRequiredMixin, SuccessMessageMixin, AjaxTemplateMixin):
    model = GroupElementYear
    context_object_name = "group_element_year"
    pk_url_kwarg = "group_element_year_id"

    # FlagMixin
    flag = "education_group_update"

    # RulesRequiredMixin
    raise_exception = True
    rules = [perms.can_change_education_group]

    def _call_rule(self, rule):
        """ The permission is computed from the education_group_year """
        return rule(self.request.user, self.education_group_year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['root'] = self.kwargs["root_id"]
        return context

    @property
    def education_group_year(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("education_group_year_id"))

    def get_root(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("root_id"))


class LearningUnitGeneric(CatalogGenericDetailView, TemplateView):
    def get_person(self):
        return get_object_or_404(Person, user=self.request.user)

    @cached_property
    def program_tree(self):
        return load_tree.load(int(self.kwargs['root_element_id']))

    @cached_property
    def node(self):
        node = self.program_tree.get_node_by_id_and_type(
            int(self.kwargs['child_element_id']),
            NodeType.LEARNING_UNIT
        )
        if node is None:
            raise Http404
        return node

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['person'] = self.get_person()
        # TODO: use DDD instead
        context['root'] = GroupYear.objects.get(element__pk=self.program_tree.root_node.pk)
        context['root_id'] = self.program_tree.root_node.pk
        context['parent'] = self.program_tree.root_node
        context['node'] = self.node
        context['tree'] = json.dumps(program_tree_view.program_tree_view_serializer(self.program_tree))
        context['group_to_parent'] = self.request.GET.get("group_to_parent") or '0'
        context['show_prerequisites'] = self.show_prerequisites(self.program_tree.root_node)
        context['selected_element_clipboard'] = self.get_selected_element_for_clipboard()

        # TODO: Remove when DDD is implemented on learning unit year...
        context['learning_unit_year'] = get_object_or_none(
            LearningUnitYear,
            element__pk=self.kwargs['child_element_id']
        )
        return context

    def show_prerequisites(self, root_node: 'NodeGroupYear'):
        return root_node.node_type not in NO_PREREQUISITES

    def get_permission_object(self):
        return GroupYear.objects.get(element__pk=self.program_tree.root_node.pk)
