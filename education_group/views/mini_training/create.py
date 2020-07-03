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

from django.views.generic import FormView
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import LoginRequiredMixin

from base.models.enums.education_group_types import MiniTrainingType
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

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context["mini_training_form"] = context["form"]
        context["tabs"] = self.get_tabs()
        context["type_text"] = MiniTrainingType.get_value(self.kwargs['type'])
        return context

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/mini_training/upsert/identification_form.html"
            }
        ]
