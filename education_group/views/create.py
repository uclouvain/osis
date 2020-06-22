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
from typing import Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.views.generic import FormView

from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import GroupType
from base.views.mixins import AjaxTemplateMixin
from education_group.forms.select_type import SelectTypeForm
from education_group.models.group_year import GroupYear


class SelectTypeCreateView(LoginRequiredMixin, AjaxTemplateMixin, FormView):
    template_name = "education_group_app/select_type_inner.html"
    form_class = SelectTypeForm

    def get(self, request, *args, **kwargs):
        if self.kwargs['category'] not in Categories.get_names():
            return HttpResponseBadRequest()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.kwargs['category'] not in Categories.get_names():
            return HttpResponseBadRequest()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            'category': self.kwargs["category"],
            'parent': self.get_parent()
        }

    def get_parent(self) -> Union[GroupYear, None]:

        try:
            parent_id = self.get_parent_id() or -1
            return GroupYear.objects.get(element__pk=parent_id)
        except GroupYear.DoesNotExist:
            pass
        return None

    def get_parent_id(self) -> str:
        """
        Parent element id will be passed in path_to queryparam
        Ex:  ...?path_to=56556|4656|565
        """
        path_to = self.request.GET.get('path_to') or ''
        return path_to.split('|')[-1]

    def form_valid(self, form):
        self.kwargs["type"] = form.cleaned_data["name"]
        return super().form_valid(form)

    def get_success_url(self):
        if self.kwargs["type"] in GroupType.get_names():
            return reverse('group_create', kwargs={'type': self.kwargs['type']})
