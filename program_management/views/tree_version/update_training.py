import functools
from typing import Dict

from django.http import Http404
from django.shortcuts import render
from django.utils.functional import cached_property
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from osis_role.contrib.views import PermissionRequiredMixin

from education_group.ddd.business_types import *
from education_group.ddd import command as command_education_group
from education_group.ddd.domain.exception import TrainingNotFoundException, GroupNotFoundException
from education_group.ddd.service.read import get_training_service, get_group_service

from program_management.ddd.business_types import *
from program_management.ddd import command
from program_management.ddd.service.read import get_program_tree_version_from_node_service
from program_management.forms import version


class TrainingVersionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'base.change_educationgroup'
    raise_exception = True

    template_name = "tree_version/training_version_update.html"

    def get(self, request, *args, **kwargs):
        context = {
            "training_version_form": self.training_version_form,
            "training_obj": self.get_training_obj(),
            "training_version_obj": self.get_program_tree_version_obj(),
            "group_obj": self.get_group_obj()
        }
        return render(request, self.template_name, context)

    @cached_property
    def training_version_form(self) -> 'version.UpdateTrainingVersionForm':
        training_identity = self.get_training_obj().entity_id
        node_identity = self.get_program_tree_obj().root_node.entity_id
        return version.UpdateTrainingVersionForm(
            data=self.request.POST or None,
            training_identity=training_identity,
            node_identity=node_identity,
            initial=self._get_training_version_form_initial_values()
        )

    @functools.lru_cache()
    def get_training_obj(self) -> 'Training':
        try:
            training_acronym = self.get_program_tree_version_obj().entity_id.offer_acronym
            get_cmd = command_education_group.GetTrainingCommand(
                acronym=training_acronym,
                year=self.kwargs['year']
            )
            return get_training_service.get_training(get_cmd)
        except TrainingNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_group_obj(self) -> 'Group':
        try:
            get_cmd = command_education_group.GetGroupCommand(
                code=self.kwargs["code"],
                year=self.kwargs["year"]
            )
            return get_group_service.get_group(get_cmd)
        except GroupNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_program_tree_version_obj(self) -> 'ProgramTreeVersion':
        get_cmd = command.GetProgramTreeVersionFromNodeCommand(
            code=self.kwargs['code'],
            year=self.kwargs['year']
        )
        return get_program_tree_version_from_node_service.get_program_tree_version_from_node(get_cmd)

    @functools.lru_cache()
    def get_program_tree_obj(self) -> 'ProgramTree':
        return self.get_program_tree_version_obj().get_tree()

    def _get_training_version_form_initial_values(self) -> Dict:
        training_version = self.get_program_tree_version_obj()
        training_obj = self.get_training_obj()
        group_obj = self.get_group_obj()

        form_initial_values = {
            'version_name': training_version.version_name,
            'title': training_version.title_fr,
            'title_english': training_version.title_en,
            'end_year': training_version.end_year_of_existence,

            "code": group_obj.code,
            "active": training_obj.status.name,
            "schedule_type": training_obj.schedule_type.name,
            "credits": training_obj.credits,
            "constraint_type": group_obj.content_constraint.type.name
            if group_obj.content_constraint.type else None,
            "min_constraint": group_obj.content_constraint.minimum,
            "max_constraint": group_obj.content_constraint.maximum,
            "offer_title_fr": training_obj.titles.title_fr,
            "offer_title_en": training_obj.titles.title_en,
            "keywords": training_obj.keywords,
            "academic_type": training_obj.academic_type.name,
            "duration": training_obj.duration,
            "duration_unit": training_obj.duration_unit.name if training_obj.duration_unit else None,
            "internship_presence": training_obj.internship_presence.name if training_obj.internship_presence else None,
            "is_enrollment_enabled": training_obj.is_enrollment_enabled,
            "has_online_re_registration": training_obj.has_online_re_registration,
            "has_partial_deliberation": training_obj.has_partial_deliberation,
            "has_admission_exam": training_obj.has_admission_exam,
            "has_dissertation": training_obj.has_dissertation,
            "produce_university_certificate": training_obj.produce_university_certificate,
            "decree_category": training_obj.decree_category.name if training_obj.decree_category else None,
            "rate_code": training_obj.rate_code.name if training_obj.rate_code else None,
            "main_language": training_obj.main_language.name,
            "english_activities": training_obj.english_activities.name if training_obj.english_activities else None,
            "other_language_activities": training_obj.other_language_activities.name
            if training_obj.other_language_activities else None,

            "main_domain": "{} - {}".format(training_obj.main_domain.decree_name, training_obj.main_domain.code)
            if training_obj.main_domain else None,
            "secondary_domains": training_obj.secondary_domains,
            "isced_domain": training_obj.isced_domain.entity_id.code if training_obj.isced_domain else None,
            "internal_comment": training_obj.internal_comment,

            "management_entity": training_obj.management_entity.acronym,
            "administration_entity": training_obj.administration_entity.acronym,
            "academic_year": training_obj.year,
            "start_year": training_obj.start_year,
            "teaching_campus": group_obj.teaching_campus.name,
            "enrollment_campus": training_obj.enrollment_campus.name,
            "other_campus_activities": training_obj.other_campus_activities.name
            if training_obj.other_language_activities else None,

            "can_be_funded": training_obj.funding.can_be_funded,
            "funding_direction": training_obj.funding.funding_orientation.name
            if training_obj.funding.funding_orientation else None,
            "can_be_international_funded": training_obj.funding.can_be_international_funded,
            "international_funding_orientation": training_obj.funding.international_funding_orientation.name
            if training_obj.funding.international_funding_orientation else None,

            "remark_fr": group_obj.remark.text_fr,
            "remark_english": group_obj.remark.text_en,

            "ares_code": training_obj.hops.ares_code if training_obj.hops else None,
            "ares_graca": training_obj.hops.ares_graca if training_obj.hops else None,
            "ares_authorization": training_obj.hops.ares_authorization if training_obj.hops else None,
            "code_inter_cfb": training_obj.co_graduation.code_inter_cfb,
            "coefficient": training_obj.co_graduation.coefficient.normalize()
            if training_obj.co_graduation.coefficient else None,

            "leads_to_diploma": training_obj.diploma.leads_to_diploma,
            "diploma_printing_title": training_obj.diploma.printing_title,
            "professional_title": training_obj.diploma.professional_title,
            "certificate_aims": [aim.code for aim in training_obj.diploma.aims]
        }
        return form_initial_values
