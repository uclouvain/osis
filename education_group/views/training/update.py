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
from typing import List, Dict, Union, Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import View

from base.utils.urls import reverse_with_get
from base.views.common import display_success_messages, display_warning_messages, display_error_messages
from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain import exception, group
from education_group.ddd.service.read import get_training_service, get_group_service, get_multiple_groups_service, \
    get_update_training_warning_messages
from education_group.enums.node_type import NodeType
from education_group.forms import training as training_forms, content as content_forms
from education_group.templatetags.academic_year_display import display_as_academic_year
from education_group.views.proxy.read import Tab
from learning_unit.ddd import command as command_learning_unit_year
from learning_unit.ddd.business_types import *
from learning_unit.ddd.domain import learning_unit_year
from learning_unit.ddd.service.read import get_multiple_learning_unit_years_service
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd import command as command_program_management
from program_management.ddd.business_types import *
from program_management.ddd.domain import exception as program_management_exception
from program_management.ddd.service.read import get_program_tree_service
from program_management.ddd.service.write import update_link_service, delete_training_with_program_tree_service, \
    update_training_with_program_tree_service, report_training_with_program_tree


class TrainingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'base.change_educationgroup'
    raise_exception = True

    template_name = "education_group_app/training/upsert/update.html"

    def get(self, request, *args, **kwargs):
        context = {
            "tabs": self.get_tabs(),
            "training_form": self.training_form,
            "content_formset": self.content_formset,
            "training_obj": self.get_training_obj(),
            "cancel_url": self.get_cancel_url(),
            "type_text": self.get_training_obj().type.value,
            "is_finality_types": self.get_training_obj().is_finality()
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        deleted_trainings = []
        updated_trainings = []
        created_trainings = []

        if self.training_form.is_valid() and self.content_formset.is_valid():
            deleted_trainings = self.delete_training()
            warning_messages = get_update_training_warning_messages.get_conflicted_fields(
                command.GetUpdateTrainingWarningMessages(
                    acronym=self.get_training_obj().acronym,
                    code=self.get_training_obj().code,
                    year=self.get_training_obj().year
                )
            )

            if not self.training_form.errors:
                updated_trainings = self.update_training()

            if warning_messages and not self.training_form.errors:
                created_trainings = self.report_training()

            if not self.training_form.errors:
                updated_links = self.update_links()

                success_messages = self.get_success_msg_updated_trainings(updated_trainings)
                success_messages += self.get_success_msg_updated_trainings(created_trainings)
                success_messages += self.get_success_msg_deleted_trainings(deleted_trainings)
                success_messages += self.get_success_msg_updated_links(updated_links)
                display_success_messages(request, success_messages, extra_tags='safe')
                display_warning_messages(request, warning_messages, extra_tags='safe')
                return HttpResponseRedirect(self.get_success_url())
        display_error_messages(self.request, self._get_default_error_messages())
        return self.get(request, *args, **kwargs)

    def get_tabs(self) -> List:
        tab_to_display = self.request.GET.get('tab', Tab.IDENTIFICATION.name)
        is_content_active = tab_to_display == Tab.CONTENT.name
        is_diploma_active = tab_to_display == Tab.DIPLOMAS_CERTIFICATES.name
        is_identification_active = not (is_content_active or is_diploma_active)
        return [
            {
                "text": _("Identification"),
                "active": is_identification_active,
                "display": True,
                "include_html": "education_group_app/training/upsert/training_identification_form.html"
            },
            {
                "text": _("Diplomas /  Certificates"),
                "active": is_diploma_active,
                "display": True,
                "include_html": "education_group_app/training/upsert/blocks/panel_diplomas_certificates_form.html"
            },
            {
                "id": "content",
                "text": _("Content"),
                "active": is_content_active,
                "display": True,
                "include_html": "education_group_app/training/upsert/content_form.html"
            }
        ]

    def get_success_url(self) -> str:
        get_data = {'path': self.request.GET['path_to']} if self.request.GET.get('path_to') else {}
        return reverse_with_get(
            'element_identification',
            kwargs={'code': self.kwargs['code'], 'year': self.kwargs['year']},
            get=get_data
        )

    def get_cancel_url(self) -> str:
        return self.get_success_url()

    def update_training(self) -> List['TrainingIdentity']:
        try:
            update_command = self._convert_form_to_update_training_command(self.training_form)
            return update_training_with_program_tree_service.update_and_report_training_with_program_tree(
                update_command
            )
        except exception.ContentConstraintTypeMissing as e:
            self.training_form.add_error("constraint_type", e.message)
        except (exception.ContentConstraintMinimumMaximumMissing,
                exception.ContentConstraintMaximumShouldBeGreaterOrEqualsThanMinimum) as e:
            self.training_form.add_error("min_constraint", e.message)
            self.training_form.add_error("max_constraint", "")
        return []

    def report_training(self) -> List['TrainingIdentity']:
        if self.get_training_obj().end_year:
            return report_training_with_program_tree.report_training_with_program_tree(
                command.PostponeTrainingWithProgramTreeCommand(
                    abbreviated_title=self.get_training_obj().acronym,
                    code=self.get_training_obj().code,
                    from_year=self.get_training_obj().end_year
                )
            )

        return []

    def delete_training(self) -> List['TrainingIdentity']:
        end_year = self.training_form.cleaned_data["end_year"]
        if not end_year:
            return []

        try:

            delete_command = self._convert_form_to_delete_trainings_command(self.training_form)
            return delete_training_with_program_tree_service.delete_training_with_program_tree(delete_command)

        except (program_management_exception.ProgramTreeNonEmpty, exception.TrainingHaveLinkWithEPC,
                exception.TrainingHaveEnrollments) as e:
            self.training_form.add_error("end_year", "")
            self.training_form.add_error(
                None,
                _("Imposible to put end date to %(end_year)s: %(msg)s") % {
                    "msg": e.message,
                    "end_year": end_year}
            )

        return []

    def update_links(self) -> List['Link']:
        update_link_commands = [
            self._convert_form_to_update_link_command(form) for form in self.content_formset.forms if form.has_changed()
        ]

        if not update_link_commands:
            return []

        cmd_bulk = command_program_management.BulkUpdateLinkCommand(
            parent_node_code=self.kwargs['code'],
            parent_node_year=self.kwargs['year'],
            update_link_cmds=update_link_commands
        )
        return update_link_service.bulk_update_links(cmd_bulk)

    def get_attach_path(self) -> Optional['Path']:
        return self.request.GET.get('path_to') or None

    @cached_property
    def training_form(self) -> 'training_forms.UpdateTrainingForm':
        return training_forms.UpdateTrainingForm(
            self.request.POST or None,
            user=self.request.user,
            training_type=self.get_training_obj().type.name,
            attach_path=self.get_attach_path(),
            initial=self._get_training_form_initial_values()
        )

    @cached_property
    def content_formset(self) -> 'content_forms.ContentFormSet':
        return content_forms.ContentFormSet(
            self.request.POST or None,
            initial=self._get_content_formset_initial_values(),
            form_kwargs=[
                {'parent_obj': self.get_group_obj(), 'child_obj': child}
                for child in self.get_children_objs()
            ]
        )

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

    def get_success_msg_updated_trainings(self, training_identites: List["TrainingIdentity"]) -> List[str]:
        return [self._get_success_msg_updated_training(identity) for identity in training_identites]

    def get_success_msg_deleted_trainings(self, trainings_identities: List['TrainingIdentity']) -> List[str]:
        return [self._get_success_msg_deleted_training(identity) for identity in trainings_identities]

    def _get_success_msg_updated_training(self, training_identity: 'TrainingIdentity') -> str:
        link = reverse_with_get(
            'education_group_read_proxy',
            kwargs={'acronym': training_identity.acronym, 'year': training_identity.year},
            get={"tab": Tab.IDENTIFICATION.value}
        )
        return _("Training <a href='%(link)s'> %(acronym)s (%(academic_year)s) </a> successfully updated.") % {
            "link": link,
            "acronym": training_identity.acronym,
            "academic_year": display_as_academic_year(training_identity.year),
        }

    def _get_success_msg_deleted_training(self, training_identity: 'TrainingIdentity') -> str:
        return _("Training %(acronym)s (%(academic_year)s) successfully deleted.") % {
            "acronym": training_identity.acronym,
            "academic_year": display_as_academic_year(training_identity.year)
        }

    def get_success_msg_updated_links(self, links: List['Link']) -> List[str]:
        messages = []

        for link in links:
            msg = _("The link of %(code)s - %(acronym)s - %(year)s has been updated.") % {
                "acronym": link.child.title,
                "code": link.entity_id.child_code,
                "year": display_as_academic_year(link.entity_id.child_year)
            }
            messages.append(msg)

        return messages

    def _get_default_error_messages(self) -> str:
        return _("Error(s) in form: The modifications are not saved")

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
            "end_year": training_obj.end_year,
            "teaching_campus": training_obj.teaching_campus.name,
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

    def _convert_form_to_update_training_command(
            self,
            form: training_forms.UpdateTrainingForm) -> command.UpdateTrainingCommand:
        cleaned_data = form.cleaned_data
        return command.UpdateTrainingCommand(
            abbreviated_title=cleaned_data['acronym'],
            code=cleaned_data['code'],
            year=cleaned_data['academic_year'].year,
            status=cleaned_data['active'],
            credits=cleaned_data['credits'],
            duration=cleaned_data['duration'],
            title_fr=cleaned_data['title_fr'],
            partial_title_fr=cleaned_data['partial_title_fr'],
            title_en=cleaned_data['title_en'],
            partial_title_en=cleaned_data['partial_title_en'],
            keywords=cleaned_data['keywords'],
            internship_presence=cleaned_data['internship_presence'],
            is_enrollment_enabled=cleaned_data['is_enrollment_enabled'],
            has_online_re_registration=cleaned_data['has_online_re_registration'],
            has_partial_deliberation=cleaned_data['has_partial_deliberation'],
            has_admission_exam=cleaned_data['has_admission_exam'],
            has_dissertation=cleaned_data['has_dissertation'],
            produce_university_certificate=cleaned_data['produce_university_certificate'],
            main_language=cleaned_data['main_language'],
            english_activities=cleaned_data['english_activities'],
            other_language_activities=cleaned_data['other_language_activities'],
            internal_comment=cleaned_data['internal_comment'],
            main_domain_code=cleaned_data['main_domain'].code if cleaned_data.get('main_domain') else None,
            main_domain_decree=cleaned_data['main_domain'].decree.name
            if cleaned_data.get('main_domain') else None,
            secondary_domains=[
                (obj.decree.name, obj.code) for obj in cleaned_data.get('secondary_domains', list())
            ],
            isced_domain_code=cleaned_data['isced_domain'].code if cleaned_data.get('isced_domain') else None,
            management_entity_acronym=cleaned_data['management_entity'],
            administration_entity_acronym=cleaned_data['administration_entity'],
            end_year=cleaned_data['end_year'].year if cleaned_data["end_year"] else None,
            teaching_campus_name=cleaned_data['teaching_campus'].name if cleaned_data["teaching_campus"] else None,
            teaching_campus_organization_name=cleaned_data['teaching_campus'].organization.name
            if cleaned_data["teaching_campus"] else None,
            enrollment_campus_name=cleaned_data['enrollment_campus'].name
            if cleaned_data["enrollment_campus"] else None,
            enrollment_campus_organization_name=cleaned_data['enrollment_campus'].organization.name
            if cleaned_data["enrollment_campus"] else None,
            other_campus_activities=cleaned_data['other_campus_activities'],
            can_be_funded=cleaned_data['can_be_funded'],
            funding_orientation=cleaned_data['funding_direction'],
            can_be_international_funded=cleaned_data['can_be_international_funded'],
            international_funding_orientation=cleaned_data['international_funding_orientation'],
            ares_code=cleaned_data['ares_code'],
            ares_graca=cleaned_data['ares_graca'],
            ares_authorization=cleaned_data['ares_authorization'],
            code_inter_cfb=cleaned_data['code_inter_cfb'],
            coefficient=cleaned_data['coefficient'],
            duration_unit=cleaned_data['duration_unit'],
            leads_to_diploma=cleaned_data['leads_to_diploma'],
            printing_title=cleaned_data['diploma_printing_title'],
            professional_title=cleaned_data['professional_title'],
            aims=[
                (aim.code, aim.section) for aim in (cleaned_data['certificate_aims'] or [])
            ],
            constraint_type=cleaned_data['constraint_type'],
            min_constraint=cleaned_data['min_constraint'],
            max_constraint=cleaned_data['max_constraint'],
            remark_fr=cleaned_data['remark_fr'],
            remark_en=cleaned_data['remark_english'],
            organization_name=cleaned_data['teaching_campus'].organization.name
            if cleaned_data["teaching_campus"] else None,
            schedule_type=cleaned_data["schedule_type"],
        )

    def _convert_form_to_delete_trainings_command(
            self,
            training_form: training_forms.UpdateTrainingForm
    ) -> command_program_management.DeleteTrainingWithProgramTreeCommand:
        cleaned_data = training_form.cleaned_data
        return command_program_management.DeleteTrainingWithProgramTreeCommand(
            code=cleaned_data["code"],
            offer_acronym=cleaned_data["acronym"],
            version_name='',
            is_transition=False,
            from_year=cleaned_data["end_year"].year+1
        )

    def _convert_form_to_update_link_command(
            self,
            form: 'content_forms.LinkForm') -> command_program_management.UpdateLinkCommand:
        return command_program_management.UpdateLinkCommand(
            child_node_code=form.child_obj.code if isinstance(form.child_obj, group.Group) else form.child_obj.acronym,
            child_node_year=form.child_obj.year,
            access_condition=form.cleaned_data.get('access_condition', False),
            is_mandatory=form.cleaned_data.get('is_mandatory', True),
            block=form.cleaned_data.get('block'),
            link_type=form.cleaned_data.get('link_type'),
            comment=form.cleaned_data.get('comment_fr'),
            comment_english=form.cleaned_data.get('comment_en'),
            relative_credits=form.cleaned_data.get('relative_credits'),
        )

    def convert_training_form_to_delete_training_command(
            self,
            training_form: training_forms.UpdateTrainingForm) -> command.DeleteTrainingCommand:
        cleaned_data = training_form.cleaned_data
        return command.DeleteTrainingCommand(
            acronym=cleaned_data["acronym"],
            from_year=cleaned_data["end_year"].year
        )

    def convert_training_form_to_delete_group_command(
            self,
            training_form: training_forms.UpdateTrainingForm) -> command.DeleteGroupCommand:
        cleaned_data = training_form.cleaned_data
        return command.DeleteGroupCommand(
            code=cleaned_data["code"],
            from_year=cleaned_data["end_year"].year
        )
