from typing import List, Dict, Union

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View

from base.models.academic_year import starting_academic_year
from base.models.campus import Campus
from base.models.enums.education_group_types import GroupType
from base.utils.cache import RequestCache
from base.views.common import display_success_messages
from education_group.ddd import command
from education_group.ddd.domain.exception import GroupCodeAlreadyExistException
from education_group.ddd.domain.group import GroupIdentity
from education_group.ddd.service.write import create_group_service
from education_group.forms.group import GroupForm
from education_group.models.group_year import GroupYear
from education_group.templatetags.academic_year_display import display_as_academic_year
from osis_role.contrib.views import PermissionRequiredMixin

from program_management.ddd import command as command_pgrm
from program_management.ddd.domain.program_tree import Path
from program_management.ddd.service.write import paste_element_service


class GroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = 'base.add_group'
    raise_exception = True

    template_name = "education_group_app/group/upsert/create.html"

    def get(self, request, *args, **kwargs):
        group_form = GroupForm(
            user=self.request.user,
            group_type=self.kwargs['type'],
            initial=self._get_initial_form()
        )
        return render(request, self.template_name, {
            "group_form": group_form,
            "tabs": self.get_tabs(),
            "type_text": GroupType.get_value(self.kwargs['type']),
            "cancel_url": self.get_cancel_url()
        })

    def _get_initial_form(self) -> Dict:
        default_campus = Campus.objects.filter(name='Louvain-la-Neuve').first()

        request_cache = RequestCache(self.request.user, reverse('version_program'))
        default_academic_year = request_cache.get_value_cached('academic_year') or starting_academic_year()
        return {
            'teaching_campus': default_campus,
            'academic_year': default_academic_year
        }

    def post(self, request, *args, **kwargs):
        group_form = GroupForm(request.POST, user=self.request.user, group_type=self.kwargs['type'])
        if group_form.is_valid():
            cmd_create = command.CreateGroupCommand(
                code=group_form.cleaned_data['code'],
                year=group_form.cleaned_data['academic_year'],
                type=self.kwargs['type'],
                abbreviated_title=group_form.cleaned_data['abbreviated_title'],
                title_fr=group_form.cleaned_data['title_fr'],
                title_en=group_form.cleaned_data['title_en'],
                credits=group_form.cleaned_data['credits'],
                constraint_type=group_form.cleaned_data['constraint_type'],
                min_constraint=group_form.cleaned_data['min_constraint'],
                max_constraint=group_form.cleaned_data['max_constraint'],
                management_entity_acronym=group_form.cleaned_data['management_entity'],
                teaching_campus_name=group_form.cleaned_data['teaching_campus']['name']
                if group_form.cleaned_data['teaching_campus'] else None,
                organization_name=group_form.cleaned_data['teaching_campus']['organization_name']
                if group_form.cleaned_data['teaching_campus'] else None,
                remark_fr=group_form.cleaned_data['remark_fr'],
                remark_en=group_form.cleaned_data['remark_en'],
                start_year=group_form.cleaned_data['academic_year'],
            )
            try:
                group_id = create_group_service.create_group(cmd_create)
                if self.get_attach_path():
                    self.__attach_group(group_id)
            except GroupCodeAlreadyExistException as e:
                group_form.add_error('code', e.message)

            if not group_form.errors:
                display_success_messages(request, self.get_success_msg(group_id), extra_tags='safe')
                return HttpResponseRedirect(self.get_success_url(group_id))

        return render(request, self.template_name, {
            "group_form": group_form,
            "tabs": self.get_tabs(),
            "type_text": GroupType.get_value(self.kwargs['type']),
            "cancel_url": self.get_cancel_url()
        })

    def __attach_group(self, group_id: GroupIdentity):
        cmd_paste = command_pgrm.PasteElementCommand(
            node_to_paste_code=group_id.code,
            node_to_paste_year=group_id.year,
            path_where_to_paste=self.get_attach_path()
        )
        paste_element_service.paste_element(cmd_paste)

    def get_success_url(self, group_id: GroupIdentity):
        url = reverse('group_identification', kwargs={'code': group_id.code, 'year': group_id.year})
        path = self.get_attach_path()
        if path:
            url += "?path={}".format(path)
        return url

    def get_success_msg(self, group_id: GroupIdentity):
        return _("Group <a href='%(link)s'> %(code)s (%(academic_year)s) </a> successfully created.") % {
            "link": self.get_success_url(group_id),
            "code": group_id.code,
            "academic_year": display_as_academic_year(group_id.year),
        }

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/group/upsert/identification_form.html"
            }
        ]

    def get_cancel_url(self) -> str:
        return reverse('version_program')

    def get_attach_path(self) -> Union[Path, None]:
        return self.request.GET.get('path_to') or None

    def get_permission_object(self) -> Union[GroupYear, None]:
        path = self.get_attach_path()
        if path:
            # Take parent from path (latest element)
            # Ex:  path: 4456|565|5656
            parent_id = path.split("|")[-1]
            try:
                return GroupYear.objects.select_related('academic_year', 'management_entity').get(element__pk=parent_id)
            except GroupYear.DoesNotExist:
                return None
        return None
