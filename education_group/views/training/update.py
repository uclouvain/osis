# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import functools
from typing import List, Dict, Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain import exception, group
from education_group.ddd.service.read import get_training_service, get_group_service, get_multiple_groups_service
from education_group.enums.node_type import NodeType
from education_group.forms import training as training_forms, content as content_forms
from learning_unit.ddd import command as command_learning_unit_year
from learning_unit.ddd.domain import learning_unit_year
from learning_unit.ddd.business_types import *
from learning_unit.ddd.service.read import get_multiple_learning_unit_years_service
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd import command as command_program_management
from program_management.ddd.business_types import *
from program_management.ddd.service.read import get_program_tree_service


class TrainingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'base.change_educationgroup'
    raise_exception = True

    template_name = "education_group_app/training/upsert/update.html"

    form_class = training_forms.UpdateTrainingForm

    def get(self, request, *args, **kwargs):
        training_form = training_forms.UpdateTrainingForm(
            user=request.user,
            training_type=self.get_training_obj().type.name,
            initial=self._get_training_form_initial_values()
        )
        content_formset = content_forms.ContentFormSet(
            initial=self._get_content_formset_initial_values(),
            form_kwargs=[
                {'parent_obj': self.get_group_obj(), 'child_obj': child}
                for child in self.get_children_objs()
            ]
        )

        context = {
            "tabs": self.get_tabs(),
            "training_form": training_form,
            "content_formset": content_formset
        }
        return render(request, self.template_name, context)

    def _get_training_form_initial_values(self) -> Dict:
        training_obj = self.get_training_obj()
        group_obj = self.get_group_obj()

        form_initial_values = {
            "acronym": training_obj.acronym,
            "code": training_obj.code,
            "active": training_obj.status.name,
            "schedule_type": training_obj.schedule_type.name,
            "credits": training_obj.credits,

            "constraint_type": group_obj.content_constraint.type.name
            if group_obj.content_constraint.type else None,
            "min_constraint": group_obj.content_constraint.minimum,
            "max_constraint": group_obj.content_constraint.maximum,

            "title_fr": training_obj.titles.title_fr,
            "partial_title_fr": training_obj.titles.partial_title_fr,
            "title_en": training_obj.titles.title_en,
            "partial_title_en": training_obj.titles.partial_title_en,
            "keywords": training_obj.keywords,

            "academic_type": training_obj.academic_type.name,
            "duration": training_obj.duration,
            "duration_unit": training_obj.duration_unit.name,
            "internship_presence": training_obj.internship_presence.name if training_obj.internship_presence else None,
            "is_enrollment_enabled": training_obj.is_enrollment_enabled,
            "has_online_re_registration": training_obj.has_online_re_registration,
            "has_partial_deliberation": training_obj.has_partial_deliberation,
            "has_admission_exam": training_obj.has_admission_exam,
            "has_dissertation": training_obj.has_dissertation,
            "produce_university_certificate": training_obj.produce_university_certificate,
            "decree_category": training_obj.decree_category.name,
            "rate_code": training_obj.rate_code.name,

            "main_language": training_obj.main_language.name,
            "english_activities": training_obj.english_activities.name,
            "other_language_activities": training_obj.other_language_activities.name,

            "main_domain": training_obj.main_domain.code,
            "secondary_domains": training_obj.secondary_domains,
            "isced_domain": training_obj.isced_domain.entity_id.code,
            "internal_comment": training_obj.internal_comment,

            "management_entity": training_obj.management_entity.acronym,
            "administration_entity": training_obj.administration_entity.acronym,
            "academic_year": training_obj.year,
            "end_year": training_obj.end_year,
            "teaching_campus": training_obj.teaching_campus.name,
            "enrollment_campus": training_obj.enrollment_campus.name,
            "other_campus_activities": training_obj.other_campus_activities.name,

            "can_be_funded": training_obj.funding.can_be_funded,
            "funding_direction": training_obj.funding.funding_orientation.name,
            "can_be_international_funded": training_obj.funding.can_be_international_funded,
            "international_funding_orientation": training_obj.funding.international_funding_orientation.name,

            "remark_fr": group_obj.remark.text_fr,
            "remark_english": group_obj.remark.text_en,

            "ares_code": training_obj.hops.ares_code,
            "ares_graca": training_obj.hops.ares_graca,
            "ares_authorization": training_obj.hops.ares_authorization,
            "code_inter_cfb": training_obj.co_graduation.code_inter_cfb,
            "coefficient": training_obj.co_graduation.coefficient,

            "leads_to_diploma": training_obj.diploma.leads_to_diploma,
            "diploma_printing_title": training_obj.diploma.printing_title,
            "professional_title": training_obj.diploma.professional_title,
            "certificate_aims": [aim.code for aim in training_obj.diploma.aims]
        }

        return form_initial_values

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

    @functools.lru_cache()
    def get_training_obj(self) -> 'Training':
        try:
            get_cmd = command.GetTrainingCommand(acronym=self.kwargs["title"], year=int(self.kwargs["year"]))
            return get_training_service.get_training(get_cmd)
        except exception.TrainingNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_group_obj(self) -> 'Group':
        try:
            get_cmd = command.GetGroupCommand(code=self.kwargs["code"], year=int(self.kwargs["year"]))
            return get_group_service.get_group(get_cmd)
        except exception.TrainingNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_program_tree_obj(self) -> 'ProgramTree':
        get_cmd = command_program_management.GetProgramTree(code=self.kwargs['code'], year=self.kwargs['year'])
        return get_program_tree_service.get_program_tree(get_cmd)

    @functools.lru_cache()
    def get_children_objs(self) -> List[Union['Group', 'LearningUnitYear']]:
        children_objs = self.__get_children_group_objs() + self.__get_children_learning_unit_year_objs()
        return sorted(
            children_objs,
            key=lambda child_obj: next(
                order for order, node in enumerate(self.get_program_tree_obj().root_node.get_direct_children_as_nodes())
                if (isinstance(child_obj, group.Group) and node.code == child_obj.code) or
                (isinstance(child_obj, learning_unit_year.LearningUnitYear) and node.code == child_obj.acronym)
            )
        )

    def __get_children_group_objs(self) -> List['Group']:
        get_group_cmds = [
            command.GetGroupCommand(code=node.code, year=node.year)
            for node
            in self.get_program_tree_obj().root_node.get_direct_children_as_nodes(
                ignore_children_from={NodeType.LEARNING_UNIT}
            )
        ]
        if get_group_cmds:
            return get_multiple_groups_service.get_multiple_groups(get_group_cmds)
        return []

    def __get_children_learning_unit_year_objs(self) -> List['LearningUnitYear']:
        get_learning_unit_cmds = [
            command_learning_unit_year.GetLearningUnitYearCommand(code=node.code, year=node.year)
            for node in self.get_program_tree_obj().root_node.get_direct_children_as_nodes(
                take_only={NodeType.LEARNING_UNIT}
            )
        ]
        if get_learning_unit_cmds:
            return get_multiple_learning_unit_years_service.get_multiple_learning_unit_years(get_learning_unit_cmds)
        return []

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/training/upsert/training_identification_form.html"
            },
            {
                "text": _("Diplomas /  Certificates"),
                "active": False,
                "display": True,
                "include_html": "education_group_app/training/upsert/blocks/panel_diplomas_certificates_form.html"
            },
            {
                "id": "content",
                "text": _("Content"),
                "active": False,
                "display": True,
                "include_html": "education_group_app/training/upsert/content_form.html"
            }
        ]
