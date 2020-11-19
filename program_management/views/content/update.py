import functools
from typing import List, Dict, Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import View

from base.forms.exceptions import InvalidFormException
from base.utils.urls import reverse_with_get
from base.views.common import display_success_messages, display_error_messages
from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain import exception
from education_group.ddd.service.read import get_group_service
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd import command as command_program_management
from program_management.ddd.business_types import *
from program_management.ddd.domain import exception as program_exception
from program_management.ddd.domain.service.get_program_tree_version_for_tree import get_program_tree_version_for_tree
from program_management.ddd.service.read import get_program_tree_service, get_program_tree_version_from_node_service
from program_management.forms import content as content_forms


class ContentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'base.change_link_data'
    raise_exception = True

    template_name = "program_management/content/update.html"

    def get(self, request, *args, **kwargs):
        context = {
            "content_formset": self.content_formset,
            "tabs": self.get_tabs(),
            "group_obj": self.get_group_obj(),
            "cancel_url": self.get_cancel_url(),
            "version": self.get_version(),
            "tree_different_versions": get_program_tree_version_for_tree(self.get_program_tree_obj().get_all_nodes())
        }
        return render(request, self.template_name, context)

    def get_version(self) -> Optional['ProgramTreeVersion']:
        try:
            get_cmd = command_program_management.GetProgramTreeVersionFromNodeCommand(
                code=self.kwargs['code'],
                year=self.kwargs['year']
            )
            return get_program_tree_version_from_node_service.get_program_tree_version_from_node(get_cmd)
        except program_exception.ProgramTreeVersionNotFoundException:
            return None

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Content"),
                "active": True,
                "display": True,
                "include_html": "program_management/content/block/panel_content.html"
            },
        ]

    def post(self, request, *args, **kwargs):
        if self.content_formset.is_valid():
            try:
                self.content_formset.save()
                success_messages = self.get_success_msg_updated_links()
                display_success_messages(request, success_messages, extra_tags='safe')
                return HttpResponseRedirect(self.get_success_url())
            except InvalidFormException:
                pass

        display_error_messages(self.request, self._get_default_error_messages())
        return self.get(request, *args, **kwargs)

    def get_success_url(self) -> str:
        get_data = {'path': self.request.GET['path_to']} if self.request.GET.get('path_to') else {}
        return reverse_with_get(
            'element_content',
            kwargs={'code': self.kwargs['code'], 'year': self.kwargs['year']},
            get=get_data
        )

    def get_cancel_url(self) -> str:
        return self.get_success_url()

    def get_attach_path(self) -> Optional['Path']:
        return self.request.GET.get('path_to') or None

    @cached_property
    def content_formset(self) -> 'content_forms.ContentFormSet':
        return content_forms.ContentFormSet(
            self.request.POST or None,
            initial=self._get_content_formset_initial_values(),
            form_kwargs=[
                {'parent_obj': self.get_program_tree_obj().root_node, 'child_obj': child}
                for child in self.get_children()
            ]
        )

    def get_group_obj(self) -> 'Group':
        try:
            get_cmd = command.GetGroupCommand(code=self.kwargs["code"], year=int(self.kwargs["year"]))
            return get_group_service.get_group(get_cmd)
        except exception.GroupNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_program_tree_obj(self) -> 'ProgramTree':
        get_cmd = command_program_management.GetProgramTree(code=self.kwargs['code'], year=self.kwargs['year'])
        return get_program_tree_service.get_program_tree(get_cmd)

    @functools.lru_cache()
    def get_children(self) -> List['Node']:
        program_tree = self.get_program_tree_obj()
        return program_tree.root_node.children_as_nodes

    def get_success_msg_updated_links(self) -> List[str]:
        return [_("The link \"%(node)s\" has been updated.") % {"node": child} for child in self.get_children()]

    def _get_default_error_messages(self) -> str:
        return _("Error(s) in form: The modifications are not saved")

    def _get_content_formset_initial_values(self) -> List[Dict]:
        children_links = self.get_program_tree_obj().root_node.children
        return [{
            'relative_credits': link.relative_credits,
            'is_mandatory': link.is_mandatory,
            'link_type': link.link_type.name if link.link_type else None,
            'access_condition': link.access_condition,
            'block': link.block,
            'comment_fr': link.comment,
            'comment_en': link.comment_english
        } for link in children_links]
