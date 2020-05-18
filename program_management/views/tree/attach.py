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
from typing import List, Tuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import formset_factory, modelformset_factory
from django.http import JsonResponse, request
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView, CreateView, FormView, TemplateView

from base.ddd.utils.validation_message import BusinessValidationMessage
from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import ElementCache
from base.views.common import display_warning_messages, display_error_messages
from base.views.education_groups import perms
from base.views.mixins import AjaxTemplateMixin
from program_management.business.group_element_years import management
from program_management.business.group_element_years.detach import DetachEducationGroupYearStrategy, \
    DetachLearningUnitYearStrategy
from program_management.business.group_element_years.management import fetch_elements_selected, fetch_source_link
from program_management.ddd.domain import program_tree
from program_management.ddd.repositories import load_node
from program_management.ddd.service import attach_node_service, command, detach_node_service
from program_management.forms.tree.attach import AttachNodeFormSet, GroupElementYearForm, \
    BaseGroupElementYearFormset, attach_form_factory, AttachToMinorMajorListChoiceForm
from program_management.models.enums.node_type import NodeType
from program_management.views.generic import GenericGroupElementYearMixin


# TODO check for permission
class AttachMultipleNodesView(LoginRequiredMixin, AjaxTemplateMixin, SuccessMessageMixin, FormView):
    template_name = "tree/attach_inner.html"

    @cached_property
    def nodes_to_attach(self) -> List[Tuple[int, NodeType]]:
        return management.fetch_nodes_selected(self.request.GET, self.request.user)

    def get_form_class(self):
        return formset_factory(form=attach_form_factory, formset=AttachNodeFormSet, extra=len(self.nodes_to_attach))

    def get_form_kwargs(self) -> List[dict]:
        return [self._get_form_kwargs(node_id, node_type) for node_id, node_type in self.nodes_to_attach]

    def _get_form_kwargs(
            self,
            node_id: int,
            node_type: NodeType
    ) -> dict:
        return {
            'node_to_attach_type': node_type,
            'node_to_attach_id': node_id,
            'path_of_node_to_attach_from': self.request.GET['path'],
        }

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(form_kwargs=self.get_form_kwargs(), data=self.request.POST or None)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["formset"] = context_data["form"]
        context_data["is_parent_a_minor_major_list_choice"] = self._is_parent_a_minor_major_list_choice(
            context_data["formset"]
        )
        context_data["nodes_by_id"] = {node_id: load_node.load_by_type(node_type, node_id)
                                       for node_id, node_type in self.nodes_to_attach}
        if not self.nodes_to_attach:
            display_warning_messages(self.request, _("Please cut or copy an item before attach it"))
        return context_data

    def form_valid(self, formset: AttachNodeFormSet):
        messages = formset.save()
        if BusinessValidationMessage.contains_errors(messages):
            return self.form_invalid(formset)
        ElementCache(self.request.user).clear()

        return super().form_valid(formset)

    def _is_parent_a_minor_major_list_choice(self, formset):
        return any(isinstance(form, AttachToMinorMajorListChoiceForm) for form in formset)

    def get_success_message(self, cleaned_data):
        return _("The content has been updated.")

    def get_success_url(self):
        return


class AttachCheckView(LoginRequiredMixin, AjaxTemplateMixin, SuccessMessageMixin, TemplateView):
    template_name = "tree/check_attach_inner.html"

    def get(self, request, *args, **kwargs):
        nodes_to_attach = management.fetch_nodes_selected(self.request.GET, self.request.user)
        check_command = command.CheckAttachNodeCommand(
            root_id=self.kwargs["root_id"],
            path_where_to_attach=self.request.GET["path"],
            nodes_to_attach=nodes_to_attach
        )
        error_messages = attach_node_service.check_attach(check_command)

        if "application/json" in self.request.headers.get("Accept", ""):
            return JsonResponse({"error_messages": [str(msg) for msg in error_messages]})

        if not error_messages:
            return redirect(
                reverse("tree_attach_node", args=[self.kwargs["root_id"]]) + "?{}".format(self.request.GET.urlencode())
            )

        display_error_messages(self.request, error_messages)
        return super().get(request, *args, **kwargs)


class PasteElementFromCacheToSelectedTreeNode(GenericGroupElementYearMixin, RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        redirect_url = reverse("check_education_group_attach", args=[self.kwargs["root_id"]])
        redirect_url = "{}?{}".format(redirect_url, self.request.GET.urlencode())

        try:
            perms.can_change_education_group(self.request.user, self.education_group_year)
        except PermissionDenied as e:
            display_warning_messages(self.request, str(e))

        cached_data = ElementCache(self.request.user).cached_data

        if cached_data:

            action_from_cache = cached_data.get('action')

            if action_from_cache == ElementCache.ElementCacheAction.CUT.value:
                link_to_detach = fetch_source_link(self.request.GET, self.request.user)  # type: GroupElementYear
                path_to_detach = "|".join([str(link_to_detach.parent.pk), str(link_to_detach.child.pk)])
                get_copy = self.request.GET.copy()  # type: request.QueryDict
                get_copy["path_to_detach"] = path_to_detach
                redirect_url = reverse("group_element_year_move", args=[self.kwargs["root_id"]])
                return "{}?{}".format(redirect_url, get_copy.urlencode())
            else:
                return redirect_url
        return super().get_redirect_url(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if self.rules:
            try:
                self.rules[0](self.request.user, self.education_group_year)

            except PermissionDenied as e:
                return render(request, 'education_group/blocks/modal/modal_access_denied.html', {'access_message': e})

        return super(PasteElementFromCacheToSelectedTreeNode, self).dispatch(request, *args, **kwargs)


class MoveGroupElementYearView(AttachMultipleNodesView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        message_list = detach_node_service.detach_node(self.request.GET["path_to_detach"], commit=False)
        if message_list.contains_errors():
            display_error_messages(self.request, message_list)
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        detach_node_service.detach_node(self.request.GET["path_to_detach"], commit=True)
        return super().form_valid(form)


def _check_attach(parent: EducationGroupYear, elements_to_attach):
    children_types = NodeType.LEARNING_UNIT \
        if elements_to_attach and isinstance(elements_to_attach[0], LearningUnitYear) else NodeType.EDUCATION_GROUP
    return attach_node_service.check_attach_via_parent(
        parent.pk,
        [element.pk for element in elements_to_attach],
        children_types
    )
