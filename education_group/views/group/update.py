import functools
from typing import List, Union, Dict

from django.http import Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render
from django.views import View
from rules.contrib.views import LoginRequiredMixin

from base.models import entity_version, academic_year, campus
from education_group.ddd import command
from education_group.ddd.domain.exception import GroupNotFoundException
from education_group.ddd.domain.group import Group
from education_group.ddd.service.read import group_service
from education_group.forms.content import ContentFormSet
from education_group.forms.group import GroupForm
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin


class GroupUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = 'base.change_educationgroup'
    raise_exception = True

    template_name = "education_group_app/group/upsert/update.html"

    def get(self, request, *args, **kwargs):
        group_form = GroupForm(
            user=self.request.user,
            group_type=self.get_group_obj().type.name,
            initial=self._get_initial_group_form()
        )
        content_formset = ContentFormSet()
        return render(request, self.template_name, {
            "group_form": group_form,
            "type_text": self.get_group_obj().type.value,
            "content_formset": content_formset,
            "tabs": self.get_tabs(),
            "cancel_url": self.get_cancel_url()
        })

    @functools.lru_cache()
    def get_group_obj(self) -> Group:
        try:
            get_cmd = command.GetGroupCommand(code=self.kwargs['code'], year=self.kwargs['year'])
            return group_service.get_group(get_cmd)
        except GroupNotFoundException:
            raise Http404

    def get_cancel_url(self) -> str:
        url = reverse('element_identification', kwargs={'code': self.kwargs['code'], 'year': self.kwargs['year']})
        if self.request.GET.get('path'):
            url += "?path={}".format(self.request.GET.get('path'))
        return url

    def _get_initial_group_form(self) -> Dict:
        group_obj = self.get_group_obj()
        return {
            'code': group_obj.code,
            'academic_year': academic_year.find_academic_year_by_year(year=group_obj.year),
            'abbreviated_title': group_obj.abbreviated_title,
            'title_fr': group_obj.titles.title_fr,
            'title_en': group_obj.titles.title_en,
            'credits': group_obj.credits,
            'constraint_type': group_obj.content_constraint.type,
            'min_constraint': group_obj.content_constraint.minimum,
            'max_constraint': group_obj.content_constraint.maximum,
            'management_entity': entity_version.find(group_obj.management_entity.acronym),
            'teaching_campus': campus.find_by_name_and_organization_name(
                name=group_obj.teaching_campus.name,
                organization_name=group_obj.teaching_campus.university_name
            ),
            'remark_fr': group_obj.remark.text_fr,
            'remark_en': group_obj.remark.text_en
        }

    def _get_initial_content_formset(self) -> Dict:
        return {}

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/group/upsert/identification_form.html"
            },
            {
                "text": _("Content"),
                "active": False,
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
