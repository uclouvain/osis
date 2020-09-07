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
from django import shortcuts
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.utils.functional import cached_property
from django.views.generic import FormView

from base.views.mixins import AjaxTemplateMixin
from education_group.models.group_year import GroupYear
from osis_common.ddd.interface import BusinessException
from program_management.ddd.command import GetNodeIdentityFromElementId
from program_management.ddd.domain import node
from program_management.ddd.domain.node import NodeGroupYear
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.service.identity_search import ProgramTreeVersionIdentitySearch
from program_management.ddd.repositories import node as node_repository
from program_management.ddd.service.read import node_identity_service
from program_management.forms.tree.update import UpdateNodeForm, UpdateNodesFormset


class UpdateLinkView(AjaxTemplateMixin, SuccessMessageMixin, FormView):
    template_name = "tree/paste_inner.html"

    # TODO : require 'change_link_data' permission for both GroupYear and LUY

    def get_form_class(self):
        return formset_factory(form=UpdateNodeForm, formset=UpdateNodesFormset)

    @cached_property
    def parent_node(self) -> dict:
        node_parent_id = int(self.request.GET['path'].split("|")[-2])
        get_node_cmd = GetNodeIdentityFromElementId(element_id=node_parent_id)
        node_parent_identity = node_identity_service.get_node_identity_from_element_id(cmd=get_node_cmd)
        if node_parent_identity:
            return {"element_code": node_parent_identity.code, "element_year": int(node_parent_identity.year)}

    @cached_property
    def node_to_update(self) -> dict:
        node_to_update_id = int(self.request.GET['path'].split("|")[-1])
        get_node_cmd = GetNodeIdentityFromElementId(element_id=node_to_update_id)
        node_to_update_identity = node_identity_service.get_node_identity_from_element_id(cmd=get_node_cmd)
        if node_to_update_identity:
            return {"element_code": node_to_update_identity.code, "element_year": int(node_to_update_identity.year)}

    def get_form_kwargs(self) -> dict:
        return {
            'node_to_update_code': self.node_to_update["element_code"],
            'node_to_update_year': self.node_to_update["element_year"],
            'to_path': self.request.GET['path'],
        }

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(form_kwargs=self.get_form_kwargs(), data=self.request.POST or None)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["formset"] = context_data.pop("form")
        context_data["is_parent_a_minor_major_option_list_choice"] = self._is_parent_a_minor_major_option_list_choice()
        context_data["nodes_by_id"] = {
            self.node_to_update["element_code"]: node_repository.NodeRepository.get(
                node.NodeIdentity(self.node_to_update["element_code"], self.node_to_update["element_year"])
            )
        }
        self._format_title_with_version(context_data["nodes_by_id"])

        for form in context_data["formset"].forms:
            node_elem = context_data["nodes_by_id"][form.node_code]
            form.initial = self._get_initial_form_kwargs(node_elem)
            form.is_group_year_form = isinstance(node_elem, NodeGroupYear)

        if len(context_data["formset"]) > 0:
            context_data['is_group_year_formset'] = context_data["formset"][0].is_group_year_form

        return context_data

    def _get_initial_form_kwargs(self, obj):
        return {
            'credits': obj.credits,
            'code': obj.code,
            'relative_credits': "%d" % (obj.credits or 0)
        }

    def _format_title_with_version(self, nodes_by_id):
        node_ele = nodes_by_id[self.node_to_update['element_code']]
        node_identity = NodeIdentity(code=self.node_to_update["element_code"], year=self.node_to_update["element_year"])
        try:
            tree_version = ProgramTreeVersionIdentitySearch().get_from_node_identity(node_identity)
            node_ele.version = tree_version.version_name
            node_ele.title = "{}[{}]".format(node_ele.title, node_ele.version) if node_ele.version else node_ele.title
        except BusinessException:
            pass

    def _is_parent_a_minor_major_option_list_choice(self):
        parent_identity = node.NodeIdentity(
            code=self.parent_node['element_code'],
            year=self.parent_node['element_year']
        )
        parent_element = node_repository.NodeRepository.get(parent_identity)
        return parent_element.is_minor_major_option_list_choice()

    def get_success_url(self):
        return
