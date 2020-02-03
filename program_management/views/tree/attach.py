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
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from django.utils.translation import gettext_lazy as _

from base.views.mixins import AjaxTemplateMixin
from program_management.forms.tree.attach import AttachNodeForm


class AttachNodeView(SuccessMessageMixin, AjaxTemplateMixin, CreateView):
    template_name = "tree/attach_confirmation.html"
    form_class = AttachNodeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_form_kwargs(self):
        # GET ELEMENT FROM CACHE for <from_path>
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_success_message(self, cleaned_data):
        return _('Attach OK')
