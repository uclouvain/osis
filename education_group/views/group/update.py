from typing import List, Union, Dict

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render
from django.views import View
from rules.contrib.views import LoginRequiredMixin

from education_group.forms.content import ContentFormSet
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin


class GroupUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = 'base.change_educationgroup'
    raise_exception = True

    template_name = "education_group_app/group/upsert/update.html"

    def get(self, request, *args, **kwargs):
        # group_form = GroupForm(
        #     user=self.request.user,
        #     group_type=self.kwargs['type'],
        #     initial=self._get_initial_form()
        # )
        group_form = None
        content_formset = ContentFormSet()
        return render(request, self.template_name, {
            "group_form": group_form,
            "content_formset": content_formset,
            "tabs": self.get_tabs(),
            "cancel_url": self.get_cancel_url()
        })

    def get_cancel_url(self) -> str:
        url = reverse('element_identification', kwargs={'code': self.kwargs['code'], 'year': self.kwargs['year']})
        if self.request.GET.get('path'):
            url += "?path={}".format(self.request.GET.get('path'))
        return url

    def _get_initial_group_form(self) -> Dict:
        return {}

    def _get_initial_content_formset(self) -> Dict:
        return {}

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/group/upsert/content_form.html"
                # "include_html": "education_group_app/group/upsert/identification_form.html"
            },
            {
                "text": _("Content"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/group/upsert/content_form.html"
            }
        ]

    def get_permission_object(self) -> Union[GroupYear, None]:
        try:
            return GroupYear.objects.select_related(
                'academic_year', 'management_entity'
            ).get(partial_acronym=self.kwargs['code'], academic_year__year=self.kwargs['year'])
        except GroupYear.DoesNotExist:
            return None
