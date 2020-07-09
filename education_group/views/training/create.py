from typing import List, Dict, Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View

from base.models.academic_year import starting_academic_year
from base.models.campus import Campus
from base.models.entity_version import find_entity_version_according_academic_year
from base.models.enums.education_group_types import GroupType, TrainingType
from base.utils.cache import RequestCache
from base.views.common import display_success_messages
from education_group.ddd import command
from education_group.ddd.domain.exception import GroupCodeAlreadyExistException, ContentConstraintTypeMissing, \
    ContentConstraintMinimumMaximumMissing, ContentConstraintMaximumShouldBeGreaterOrEqualsThanMinimum
from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.service.write import create_training_service
from education_group.forms.training import CreateTrainingForm
from education_group.templatetags.academic_year_display import display_as_academic_year
from education_group.views.proxy.read import Tab
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.domain.program_tree import Path


class TrainingCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = 'base.add_training'
    raise_exception = True

    template_name = "education_group_app/training/upsert/create.html"

    def get(self, request, *args, **kwargs):
        training_form = CreateTrainingForm(
            user=self.request.user,
            training_type=self.kwargs['type'],
            initial=self._get_initial_form(),
        )
        return render(request, self.template_name, {
            "training_form": training_form,
            "tabs": self.get_tabs(),
            "type_text": TrainingType.get_value(self.kwargs['type'])
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
        training_form = CreateTrainingForm(data=request.POST, user=self.request.user, training_type=self.kwargs['type'])
        if training_form.is_valid():
            create_training_cmd = command.CreateTrainingCommand(
                abbreviated_title=training_form.cleaned_data['acronym'],
                status=training_form.cleaned_data['active'],
                code=training_form.cleaned_data['code'],
                year=training_form.cleaned_data['academic_year'].year,
                type=self.kwargs['type'],
                credits=training_form.cleaned_data['credits'],
                schedule_type=training_form.cleaned_data['schedule_type'],
                duration=training_form.cleaned_data['duration'],
                start_year=training_form.cleaned_data['academic_year'].year,
                title_fr=training_form.cleaned_data['title_fr'],
                partial_title_fr=training_form.cleaned_data['partial_title_fr'],
                title_en=training_form.cleaned_data['title_en'],
                partial_title_en=training_form.cleaned_data['partial_title_en'],
                keywords=training_form.cleaned_data['keywords'],
                internship=training_form.cleaned_data['internship'],
                is_enrollment_enabled=training_form.cleaned_data['is_enrollment_enabled'],
                has_online_re_registration=training_form.cleaned_data['has_online_re_registration'],
                has_partial_deliberation=training_form.cleaned_data['has_partial_deliberation'],
                has_admission_exam=training_form.cleaned_data['has_admission_exam'],
                has_dissertation=training_form.cleaned_data['has_dissertation'],
                produce_university_certificate=training_form.cleaned_data['produce_university_certificate'],
                decree_category=training_form.cleaned_data['decree_category'],
                rate_code=training_form.cleaned_data['rate_code'],
                main_language=training_form.cleaned_data['main_language'],
                english_activities=training_form.cleaned_data['english_activities'],
                other_language_activities=training_form.cleaned_data['other_language_activities'],
                internal_comment=training_form.cleaned_data['internal_comment'],
                main_domain_code=training_form.cleaned_data['main_domain'].code
                if training_form.cleaned_data['main_domain'] else None,
                main_domain_decree=training_form.cleaned_data['main_domain'].decree.name
                if training_form.cleaned_data['main_domain'] else None,
                secondary_domains=[
                    (obj.decree.name, obj.code) for obj in training_form.cleaned_data['secondary_domains']
                ],
                isced_domain_code=training_form.cleaned_data['isced_domain'].code
                if training_form.cleaned_data['isced_domain'] else None,
                management_entity_acronym=training_form.cleaned_data['management_entity'],
                administration_entity_acronym=training_form.cleaned_data['administration_entity'],
                end_year=training_form.cleaned_data['end_year'].year
                if training_form.cleaned_data['end_year'] else None,
                teaching_campus_name=training_form.cleaned_data['teaching_campus'].name,
                teaching_campus_organization_name=training_form.cleaned_data['teaching_campus'].organization.name,
                enrollment_campus_name=training_form.cleaned_data['enrollment_campus'].name,
                enrollment_campus_organization_name=training_form.cleaned_data['enrollment_campus'].organization.name,
                other_campus_activities=training_form.cleaned_data['other_campus_activities'],
                can_be_funded=training_form.cleaned_data['can_be_funded'],
                funding_orientation=training_form.cleaned_data['funding_direction'],
                can_be_international_funded=training_form.cleaned_data['can_be_international_funded'],
                international_funding_orientation=training_form.cleaned_data['international_funding_orientation'],
                ares_code=training_form.cleaned_data['ares_code'],
                ares_graca=training_form.cleaned_data['ares_graca'],
                ares_authorization=training_form.cleaned_data['ares_authorization'],
                code_inter_cfb=training_form.cleaned_data['code_inter_cfb'],
                coefficient=training_form.cleaned_data['coefficient'],
                academic_type=training_form.cleaned_data['academic_type'],
                duration_unit=training_form.cleaned_data['duration_unit'],
                leads_to_diploma=training_form.cleaned_data['leads_to_diploma'],
                printing_title=training_form.cleaned_data['diploma_printing_title'],
                professional_title=training_form.cleaned_data['professional_title'],
                aims=[
                    (aim.code, aim.section) for aim in (training_form.cleaned_data['certificate_aims'] or [])
                ],
                constraint_type=training_form.cleaned_data['constraint_type'],
                min_constraint=training_form.cleaned_data['min_constraint'],
                max_constraint=training_form.cleaned_data['max_constraint'],
                remark_fr=training_form.cleaned_data['remark_fr'],
                remark_en=training_form.cleaned_data['remark_english'],
            )
            try:
                if self.get_attach_path():
                    training_id = None
                    # create_and_attach_training_cmd = CreateAndAttachTrainingCommand(
                    #     **create_training_cmd
                    # )
                    # training_id = create_and_attach_training_service.create_and_attach_training(create_training_cmd)
                else:
                    training_id = create_training_service.create_orphan_training(create_training_cmd)

            except GroupCodeAlreadyExistException as e:
                training_form.add_error('code', e.message)
            except ContentConstraintTypeMissing as e:
                training_form.add_error('constraint_type', e.message)
            except (ContentConstraintMinimumMaximumMissing, ContentConstraintMaximumShouldBeGreaterOrEqualsThanMinimum) \
                    as e:
                training_form.add_error('min_constraint', e.message)
                training_form.add_error('max_constraint', '')
            # except Exception as e:
            #     training_form._errors.append(str(e))

            if not training_form.errors:
                display_success_messages(request, self.get_success_msg(training_id), extra_tags='safe')
                return HttpResponseRedirect(self.get_success_url(training_id))

        return render(request, self.template_name, {
            "training_form": training_form,
            "tabs": self.get_tabs(),
            "type_text": GroupType.get_value(self.kwargs['type'])
        })

    def get_success_url(self, training_id: TrainingIdentity):
        url = reverse(
            'education_group_read_proxy',
            kwargs={'acronym': training_id.acronym, 'year': training_id.year}
        ) + '?tab={}'.format(Tab.IDENTIFICATION)
        path = self.get_attach_path()
        if path:
            url += "?path={}".format(path)
        return url

    def get_success_msg(self, training_id: TrainingIdentity):
        return _("Training <a href='%(link)s'> %(acronym)s (%(academic_year)s) </a> successfully created.") % {
            "link": self.get_success_url(training_id),
            "acronym": training_id.acronym,
            "academic_year": display_as_academic_year(training_id.year),
        }

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
        ]

    def get_attach_path(self) -> Union[Path, None]:
        return self.request.GET.get('path_to') or None

    # TODO :: how to manage permissions when need to check for EducationGroupYear (create) + GroupYear (create + attach)?
    # def get_permission_object(self) -> Union[EducationGroupYear, None]:
    #     path = self.get_attach_path()
    #     if path:
    #         # Take parent from path (latest element)
    #         # Ex:  path: 4456|565|5656
    #         parent_id = path.split("|")[-1]
    #         try:
    #             return GroupYear.objects.get(element__pk=parent_id)
    #         except GroupYear.DoesNotExist:
    #             return None
    #     return None
