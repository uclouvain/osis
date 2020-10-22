##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import functools
from typing import List

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View

from base.models.enums import education_group_categories
from base.models.utils.utils import ChoiceEnum
from base.views.common import display_success_messages
from base.views.mixins import AjaxTemplateMixin
from education_group.ddd.domain import exception
from education_group.ddd.domain.training import TrainingIdentity
from education_group.models.group_year import GroupYear
from education_group.templatetags.academic_year_display import display_as_academic_year
from osis_role.contrib.views import AjaxPermissionRequiredMixin
from program_management.ddd.business_types import *
from program_management.ddd.command import CreateProgramTreeVersionCommand, ExtendProgramTreeVersionCommand, \
    UpdateProgramTreeVersionCommand, PostponeProgramTreeVersionCommand, ProlongExistingProgramTreeVersionCommand
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.service.identity_search import NodeIdentitySearch, ProgramTreeVersionIdentitySearch
from program_management.ddd.service.write import create_and_postpone_tree_version_service, \
    extend_existing_tree_version_service, update_program_tree_version_service, \
    postpone_tree_version_service, prolong_existing_tree_version_service
from program_management.forms.version import SpecificVersionForm
from program_management.views.tree_version.check_version_name import get_last_existing_version


class CreateProgramTreeVersionType(ChoiceEnum):
    NEW_VERSION = "new_version"
    EXTEND = "extend"


class CreateProgramTreeVersion(AjaxPermissionRequiredMixin, AjaxTemplateMixin, View):
    template_name = "tree_version/create_specific_version_inner.html"
    form_class = SpecificVersionForm

    @cached_property
    def node_identity(self) -> 'NodeIdentity':
        return NodeIdentity(code=self.kwargs['code'], year=self.kwargs['year'])

    @cached_property
    def training_identity(self) -> 'TrainingIdentity':
        return TrainingIdentity(acronym=self.tree_version_identity.offer_acronym, year=self.tree_version_identity.year)

    @cached_property
    def tree_version_identity(self) -> 'ProgramTreeVersionIdentity':
        return ProgramTreeVersionIdentitySearch().get_from_node_identity(self.node_identity)

    @cached_property
    def person(self):
        return self.request.user.person

    @functools.lru_cache()
    def get_permission_object(self) -> GroupYear:
        return get_object_or_404(
            GroupYear,
            academic_year__year=self.kwargs['year'],
            partial_acronym=self.kwargs['code'],
        )

    def get_permission_required(self):
        if self.get_permission_object().education_group_type.category == education_group_categories.TRAINING:
            return ("base.add_training_version",)
        return ("base.add_minitraining_version",)

    def get(self, request, *args, **kwargs):
        form = SpecificVersionForm(tree_version_identity=self.tree_version_identity)
        return render(request, self.template_name, self.get_context_data(form))

    def post(self, request, *args, **kwargs):
        form = SpecificVersionForm(tree_version_identity=self.tree_version_identity, data=request.POST)
        if form.is_valid():
            last_existing_version = get_last_existing_version(
                version_name=form.cleaned_data['version_name'],
                offer_acronym=self.tree_version_identity.offer_acronym,
            )

            identities = []
            if not last_existing_version:
                command = _convert_form_to_create_command(form)
                try:
                    identities = create_and_postpone_tree_version_service.create_and_postpone(command=command)
                except (exception.VersionNameAlreadyExist, exception.MultipleEntitiesFoundException) as e:
                    form.add_error('version_name', e.message)
            else:
                identities = prolong_existing_tree_version_service.prolong_existing_tree_version(
                    _convert_form_to_prolong_command(form)
                )

            if not form.errors:
                self._display_success_messages(identities)
                node_identity = NodeIdentitySearch().get_from_tree_version_identity(identities[0])
                url = reverse(
                    "element_identification",
                    kwargs={'year': self.node_identity.year, 'code': node_identity.code}
                )
                return JsonResponse({
                    'success_url': url
                })
        return render(request, self.template_name, self.get_context_data(form))

    def get_context_data(self, form: SpecificVersionForm):
        return {
            'training_identity': self.training_identity,
            'node_identity': self.node_identity,
            'form': form,
        }

    def get_url_program_version(self, created_version_id: 'ProgramTreeVersionIdentity'):
        node_identity = NodeIdentitySearch().get_from_tree_version_identity(created_version_id)
        return reverse(
            "element_identification",
            kwargs={
                'year': node_identity.year,
                'code': node_identity.code,
            }
        )

    def _display_success_messages(self, identities: List['ProgramTreeVersionIdentity']):
        success_messages = []
        for created_identity in identities:
            success_messages.append(
                _(
                    "Specific version for education group year "
                    "<a href='%(link)s'> %(offer_acronym)s[%(acronym)s] (%(academic_year)s) </a> successfully created."
                ) % {
                    "link": self.get_url_program_version(created_identity),
                    "offer_acronym": created_identity.offer_acronym,
                    "acronym": created_identity.version_name,
                    "academic_year": display_as_academic_year(created_identity.year)
                }
            )
        display_success_messages(self.request, success_messages, extra_tags='safe')


def _convert_form_to_create_command(form: SpecificVersionForm) -> CreateProgramTreeVersionCommand:
    return CreateProgramTreeVersionCommand(
        offer_acronym=form.tree_version_identity.offer_acronym,
        version_name=form.cleaned_data.get("version_name"),
        year=form.tree_version_identity.year,
        is_transition=False,
        title_en=form.cleaned_data.get("version_title_en"),
        title_fr=form.cleaned_data.get("version_title_fr"),
        end_year=form.cleaned_data.get("end_year"),
    )


def _convert_form_to_prolong_command(form: SpecificVersionForm) -> ProlongExistingProgramTreeVersionCommand:
    return ProlongExistingProgramTreeVersionCommand(
        end_year=form.cleaned_data.get("end_year"),
        updated_year=form.tree_version_identity.year,
        offer_acronym=form.tree_version_identity.offer_acronym,
        version_name=form.cleaned_data['version_name'],
        is_transition=False,
        title_en=form.cleaned_data.get("version_title_en"),
        title_fr=form.cleaned_data.get("version_title_fr"),
    )
