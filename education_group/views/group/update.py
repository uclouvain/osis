import functools
from typing import List, Union, Dict

from django.http import Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render
from django.views import View
from rules.contrib.views import LoginRequiredMixin

import education_group.ddd.service.read.get_multiple_groups_service
from base.models import entity_version, academic_year, campus
from education_group.ddd import command
from learning_unit.ddd import command as command_learning_unit_year
from learning_unit.ddd.domain.learning_unit_year import LearningUnitYear
from learning_unit.ddd.service.read import get_multiple_learning_unit_years_service
from program_management.ddd import command as command_program_management
from education_group.ddd.domain.exception import GroupNotFoundException
from education_group.ddd.domain.group import Group
from education_group.ddd.service.read import get_group_service
from education_group.forms.content import ContentFormSet
from education_group.forms.group import GroupUpdateForm
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.ddd.service.read import get_program_tree_service
from program_management.models.enums.node_type import NodeType


class GroupUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = 'base.change_educationgroup'
    raise_exception = True

    template_name = "education_group_app/group/upsert/update.html"

    def get(self, request, *args, **kwargs):
        group_form = GroupUpdateForm(
            user=self.request.user,
            group_type=self.get_group_obj().type.name,
            initial=self._get_initial_group_form()
        )
        content_formset = ContentFormSet(
            initial=self._get_initial_content_formset(),
            form_kwargs=[
                {'parent_obj': self.get_group_obj(), 'child_obj': child}
                for child in self.get_children_objs()
            ],
        )
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
            return get_group_service.get_group(get_cmd)
        except GroupNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_program_tree_obj(self) -> ProgramTree:
        get_pgrm_tree_cmd = command_program_management.GetProgramTree(
            code=self.kwargs['code'],
            year=self.kwargs['year']
        )
        return get_program_tree_service.get_program_tree(get_pgrm_tree_cmd)

    @functools.lru_cache()
    def get_children_objs(self) -> List[Union[Group, LearningUnitYear]]:
        children_objs = self.__get_children_group_obj() + self.__get_children_learning_unit_year_obj()
        return sorted(
            children_objs,
            key=lambda child_obj: next(
                order for order, node in enumerate(self.get_program_tree_obj().root_node.get_direct_children_as_nodes())
                if (isinstance(child_obj, Group) and node.code == child_obj.code) or
                   (isinstance(child_obj, LearningUnitYear) and node.code == child_obj.acronym)
            )
        )

    def __get_children_group_obj(self) -> List[Group]:
        get_group_cmds = [
            command.GetGroupCommand(code=node.code, year=node.year)
            for node in self.get_program_tree_obj().root_node.get_direct_children_as_nodes(
                ignore_children_from={NodeType.LEARNING_UNIT}
            )
        ]
        if get_group_cmds:
            return education_group.ddd.service.read.get_multiple_groups_service.get_multiple_groups(get_group_cmds)
        return []

    def __get_children_learning_unit_year_obj(self) -> List[LearningUnitYear]:
        get_learning_unit_cmds = [
            command_learning_unit_year.GetLearningUnitYearCommand(code=node.code, year=node.year)
            for node in self.get_program_tree_obj().root_node.get_direct_children_as_nodes(
                take_only={NodeType.LEARNING_UNIT}
            )
        ]
        if get_learning_unit_cmds:
            return get_multiple_learning_unit_years_service.get_multiple_learning_unit_years(get_learning_unit_cmds)
        return []

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

    def _get_initial_content_formset(self) -> List[Dict]:
        children_links = self.get_program_tree_obj().root_node.children
        return [{
            'relative_credits': link.relative_credits,
            'is_mandatory': link.is_mandatory,
            'link_type': link.link_type,
            'access_condition': link.access_condition,
            'block': link.block,
            'comment_fr': link.comment,
            'comment_en': link.comment_english
        } for link in children_links]

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
                "display": bool(self.get_program_tree_obj().root_node.get_all_children()),
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
