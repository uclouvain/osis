from typing import List

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View

from base.models.enums.education_group_types import GroupType
from base.views.common import display_success_messages
from education_group.ddd import command
from education_group.ddd.domain.group import GroupIdentity
from education_group.ddd.service.write import group_service
from education_group.forms.group import GroupForm
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin


class GroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = 'base.add_group'
    raise_exception = True

    template_name = "education_group_app/group/upsert/create.html"

    def get(self, request, *args, **kwargs):
        group_form = GroupForm(user=self.request.user, group_type=self.kwargs['type'])
        return render(request, self.template_name, {
            "group_form": group_form,
            "tabs": self.get_tabs(),
            "type_text": GroupType.get_value(self.kwargs['type'])
        })

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
                teaching_campus_name=group_form.cleaned_data['teaching_campus']['name'],
                organization_name=group_form.cleaned_data['teaching_campus']['organization_name'],
                remark_fr=group_form.cleaned_data['remark_fr'],
                remark_en=group_form.cleaned_data['remark_en'],
                start_year=group_form.cleaned_data['academic_year'],
            )
            group_id = group_service.create_group(cmd_create)
            display_success_messages(request, self.get_success_msg(group_id))
            return HttpResponseRedirect(self.get_success_url(group_id))

        return render(request, self.template_name, {
            "group_form": group_form,
            "tabs": self.get_tabs(),
            "type_text": GroupType.get_value(self.kwargs['type'])
        })

    def get_success_url(self, group_id: GroupIdentity):
        return reverse('group_identification', kwargs={'code': group_id.code, 'year': group_id.year})

    def get_success_msg(self, group_id: GroupIdentity):
        return _("Group <a href='%(link)s'> %(code)s (%(academic_year)s) </a> successfully created.") % {
            "link": self.get_success_url(group_id),
            "code": group_id.code,
            "academic_year": group_id.year,
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

    def get_parent_identity(self):
        """
        Find the parent identity from 'attach_to' querypart
        Ex:  <...>?attach_to=<CODE>_<YEAR>
        """
        id_raw = self.request.GET.get('attach_to', '').split("_")
        if len(id_raw) == 2:
            return GroupIdentity(code=id_raw[0], year=int(id_raw[1]))
        return None

    def get_permission_object(self):
        parent_id = self.get_parent_identity()
        if parent_id:
            try:
                return GroupYear.objects.get(
                    partial_acronym=parent_id.code,
                    academic_year__year=parent_id.year
                )
            except GroupYear.DoesNotExist:
                return None
        return None
