from typing import List

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View

from education_group.forms.group import GroupForm
from osis_role.contrib.views import PermissionRequiredMixin


class GroupCreateView(
    LoginRequiredMixin,
    # PermissionRequiredMixin,
    View
):
    # PermissionRequiredMixin
    # permission_required = 'base.add_group'
    # raise_exception = True

    template_name = "education_group_app/group/upsert/create.html"

    def get(self, request, *args, **kwargs):
        group_form = GroupForm(user=self.request.user)
        return render(request, self.template_name, {
            "group_form": group_form,
            "tabs": self.get_tabs()
        })

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/group/upsert/identification_form.html"
            }
        ]

    def get_permission_object(self):
        return None
