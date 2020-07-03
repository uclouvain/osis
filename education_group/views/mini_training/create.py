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
from typing import List, Dict, Type

from django.http import response
from django.urls import reverse
from django.views.generic import FormView
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import LoginRequiredMixin

from base.models.enums.education_group_types import MiniTrainingType
from education_group.ddd import command
from education_group.ddd.service.write import create_mini_training_service
from education_group.forms import mini_training as mini_training_form
from osis_role.contrib.views import PermissionRequiredMixin


class MiniTrainingCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'base.add_minitraining'
    raise_exception = True

    template_name = "education_group_app/mini_training/upsert/create.html"

    def get_form_class(self) -> Type[mini_training_form.MiniTrainingForm]:
        return mini_training_form.MiniTrainingForm

    def get_form_kwargs(self) -> Dict:
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        form_kwargs["mini_training_type"] = self.kwargs['type']
        return form_kwargs

    #  TODO incorporate type in mini training form
    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context["mini_training_form"] = context["form"]
        context["tabs"] = self.get_tabs()
        context["type_text"] = MiniTrainingType.get_value(self.kwargs['type'])
        return context

    def form_valid(self, form: mini_training_form.MiniTrainingForm) -> response.HttpResponseBase:
        create_command = command.CreateOrphanMiniTrainingCommand(
            code=form.cleaned_data['code'],
            year=form.cleaned_data['year'],
            type=self.kwargs['type'],
            abbreviated_title=form.cleaned_data['abbreviated_title'],
            title_fr=form.cleaned_data['title_fr'],
            title_en=form.cleaned_data['title_en'],
            status=form.cleaned_data['status'],
            schedule_type=form.cleaned_data['schedule_type'],
            credits=form.cleaned_data['credits'],
            constraint_type=form.cleaned_data['constraint_type'],
            min_constraint=form.cleaned_data['min_constraint'],
            max_constraint=form.cleaned_data['max_constraint'],
            management_entity_acronym=form.cleaned_data['management_entity_acronym'],
            teaching_campus_name=form.cleaned_data['teaching_campus_name'],
            organization_name=form.cleaned_data['organization_name'],
            remark_fr=form.cleaned_data['remark_fr'],
            remark_en=form.cleaned_data['remark_en'],
            start_year=form.cleaned_data['start_year'],
            end_year=form.cleaned_data['end_year'],
        )
        create_mini_training_service.create_orphan_mini_training(create_command)
        return super().form_valid(form)

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/mini_training/upsert/identification_form.html"
            }
        ]

    def get_success_url(self) -> str:
        return reverse("home")
