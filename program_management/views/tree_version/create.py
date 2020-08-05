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
import re

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import CreateView

from base.forms.education_group.version import SpecificVersionForm
from base.models.education_group_year import EducationGroupYear
from base.views.common import display_success_messages
from base.views.mixins import AjaxTemplateMixin
from education_group.ddd.domain.service.identity_search import TrainingIdentitySearch
from education_group.ddd.domain.training import TrainingIdentity
from education_group.models.group_year import GroupYear
from osis_common.decorators.ajax import ajax_required
from osis_role.contrib.views import AjaxPermissionRequiredMixin
from program_management.ddd.domain.node import NodeIdentity
from program_management.models.education_group_version import EducationGroupVersion


class CreateProgramTreeVersion(AjaxPermissionRequiredMixin, SuccessMessageMixin, AjaxTemplateMixin, CreateView):
    template_name = "tree_version/create_specific_version_inner.html"
    form_class = SpecificVersionForm
    permission_required = 'base.create_specific_version'

    @cached_property
    def node_identity(self) -> 'NodeIdentity':
        return NodeIdentity(code=self.kwargs['code'], year=self.kwargs['year'])

    @cached_property
    def training_identity(self) -> 'TrainingIdentity':
        return TrainingIdentitySearch().get_from_node_identity(self.node_identity)

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def education_group_year(self):
        return get_object_or_404(
            EducationGroupYear,
            academic_year__year=self.kwargs['year'],
            acronym=self.kwargs['code'],
        )

    def _call_rule(self, rule):
        return rule(self.person, self.education_group_year)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["save_type"] = self.request.POST.get("save_type")
        form_kwargs['education_group_year'] = self.education_group_year
        form_kwargs.pop('instance')
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateProgramTreeVersion, self).get_context_data(**kwargs)
        context['training_identity'] = self.training_identity
        context['node_identity'] = self.node_identity
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get_success_message(self, cleaned_data):
        display_success_messages(self.request, cleaned_data["messages"])

    def get_success_url(self):
        return reverse(
            "training_identification",
            args=[
                self.education_group_year.academic_year.year,
                self.education_group_year.partial_acronym,
            ]
        )


@login_required
@ajax_required
def check_version_name(request, year, code):
    version_name = request.GET['version_name']
    existed_version_name = False
    existing_version_name = check_existing_version(version_name, year, code)
    last_using = None
    if existing_version_name:
        old_specific_versions = find_last_existed_version(version_name, year, code)
        if old_specific_versions:
            last_using = str(old_specific_versions.offer.academic_year)
            existed_version_name = True
    valid = bool(re.match("^[A-Z]{0,15}$", request.GET['version_name'].upper()))
    return JsonResponse({
        "existed_version_name": existed_version_name,
        "existing_version_name": existing_version_name,
        "last_using": last_using,
        "valid": valid,
        "version_name": request.GET['version_name']}, safe=False)


def check_existing_version(version_name: str, year: int, code: str) -> bool:
    return EducationGroupVersion.objects.filter(
        version_name=version_name,
        root_group__academic_year__year=year,
        root_group__acronym=code
    ).exists()


def find_last_existed_version(version_name, year, code):
    return EducationGroupVersion.objects.filter(
        version_name=version_name,
        root_group__academic_year__year=year,
        root_group__acronym=code,
    ).order_by(
        'offer__academic_year'
    ).last()
