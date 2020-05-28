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
from typing import List, Optional

from django import shortcuts
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

import program_management.ddd.command
from base.models.education_group_year import EducationGroupYear
from base.utils.cache import ElementCache
from base.views.common import display_warning_messages, display_error_messages
from base.views.mixins import AjaxTemplateMixin
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.repositories import load_node
from program_management.ddd.service import attach_node_service
from program_management.ddd.service.read import element_selected_service
from program_management.forms.tree.paste import PasteNodesFormset, paste_form_factory, PasteToMinorMajorListChoiceForm


class PasteNodesView(PermissionRequiredMixin, AjaxTemplateMixin, SuccessMessageMixin, FormView):
    template_name = "tree/paste_inner.html"
    permission_required = "base.attach_educationgroup"

    def has_permission(self):
        return self._has_permission_to_detach() & super().has_permission()

    def _has_permission_to_detach(self) -> bool:
        nodes_to_detach_from = [
            int(path_to_detach.split("|")[-2]) for code, year, path_to_detach in self.nodes_to_paste if path_to_detach
        ]
        objs_to_detach_from = EducationGroupYear.objects.filter(id__in=nodes_to_detach_from)
        return all(self.request.user.has_perms(("base.detach_educationgroup",), obj_to_detach)
                   for obj_to_detach in objs_to_detach_from)

    def get_permission_object(self) -> EducationGroupYear:
        node_to_paste_to_id = int(self.request.GET['path'].split("|")[-1])
        return shortcuts.get_object_or_404(EducationGroupYear, pk=node_to_paste_to_id)

    @cached_property
    def nodes_to_paste(self) -> List[dict]:
        return [element_selected_service.retrieve_element_selected(self.request.user.id)]

    def get_form_class(self):
        return formset_factory(form=paste_form_factory, formset=PasteNodesFormset, extra=len(self.nodes_to_paste))

    def get_form_kwargs(self) -> List[dict]:
        return [self._get_form_kwargs(node_code, node_year, path_to_detach)
                for node_code, node_year, path_to_detach in self.nodes_to_paste]

    def _get_form_kwargs(
            self,
            node_code: str,
            node_year: int,
            path_to_detach: Optional[str]
    ) -> dict:
        return {
            'node_to_paste_code': node_code,
            'node_to_paste_year': node_year,
            'path_of_node_to_paste_into': self.request.GET['path'],
            'path_to_detach': path_to_detach,
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
                                       for node_id, node_type, source_parent in self.nodes_to_paste}
        if not self.nodes_to_paste:
            display_warning_messages(self.request, _("Please cut or copy an item before paste"))
        return context_data

    def form_valid(self, formset: PasteNodesFormset):
        node_entities_ids = formset.save()
        if None in node_entities_ids:
            return self.form_invalid(formset)
        ElementCache(self.request.user).clear()

        return super().form_valid(formset)

    def _is_parent_a_minor_major_list_choice(self, formset):
        return any(isinstance(form, PasteToMinorMajorListChoiceForm) for form in formset)

    def get_success_message(self, cleaned_data):
        return _("The content has been updated.")

    def get_success_url(self):
        return


class CheckPasteView(LoginRequiredMixin, AjaxTemplateMixin, SuccessMessageMixin, TemplateView):
    template_name = "tree/check_paste_inner.html"

    def get(self, request, *args, **kwargs):
        nodes_to_paste = element_selected_service.retrieve_element_selected(
            self.request.user,
            self.request.GET.get("id", []),
            self.request.GET.get("content_type")
        )
        check_command = program_management.ddd.command.CheckAttachNodeCommand(
            root_id=self.kwargs["root_id"],
            path_where_to_attach=self.request.GET["path"],
            nodes_to_attach=nodes_to_paste
        )
        error_messages = attach_node_service.check_attach(check_command)

        if "application/json" in self.request.headers.get("Accept", ""):
            return JsonResponse({"error_messages": [str(msg) for msg in error_messages]})

        if not error_messages:
            return redirect(
                reverse("tree_paste_node", args=[self.kwargs["root_id"]]) + "?{}".format(self.request.GET.urlencode())
            )

        display_error_messages(self.request, error_messages)
        return super().get(request, *args, **kwargs)
