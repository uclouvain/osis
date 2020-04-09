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
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from base.utils.cache import ElementCache
from base.views.common import display_business_messages
from base.views.common import display_error_messages, display_warning_messages
from base.views.mixins import AjaxTemplateMixin, RulesRequiredMixin
from program_management.ddd.domain.program_tree import PATH_SEPARATOR
from program_management.ddd.service import detach_node_service
from program_management.forms.tree.detach import DetachNodeForm
from program_management.views import perms as group_element_year_perms
from program_management.views.generic import GenericGroupElementYearMixin


class DetachNodeView(GenericGroupElementYearMixin, AjaxTemplateMixin, FormView):
    template_name = "tree/detach_confirmation_inner.html"
    form_class = DetachNodeForm

    raise_exception = True
    rules = [group_element_year_perms.can_detach_group_element_year]
    # partial_reload = True

    # def get_form_kwargs(self):
    #     return {
    #         **super().get_form_kwargs(),
    #         'path_to_detach': self.request.POST.get('path_to_detach')
    #     }

    def _call_rule(self, rule):
        return rule(self.request.user, self.get_object())

    def get_context_data(self, **kwargs):
        context = super(DetachNodeView, self).get_context_data(**kwargs)
        message_list = detach_node_service.detach_node(self.request.GET.get('path'), commit=False)
        display_warning_messages(self.request, message_list.warnings)
        display_error_messages(self.request, message_list.errors)
        context['detach_ok'] = not message_list.contains_errors()
        return context

    def get_initial(self):
        print()
        return {
            **super().get_initial(),
            'path': self.request.GET.get('path')
        }

    def form_valid(self, form):
        message_list = form.save()
        display_business_messages(self.request, message_list.messages)
        self._remove_element_from_clipboard_if_stored(form.cleaned_data['path'])
        return super().form_valid(form)

    def _remove_element_from_clipboard_if_stored(self, path: str):
        element_cache = ElementCache(self.request.user)
        detached_element_id = int(path.split(PATH_SEPARATOR)[-1])
        if element_cache.equals(detached_element_id):
            element_cache.clear()

    def get_success_url(self):
        return

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                for rule in self.rules:
                    perm = rule(self.request.user, self.get_object())
                    if not perm:
                        break

            except PermissionDenied as e:

                return render(request,
                              'education_group/blocks/modal/modal_access_denied.html',
                              {'access_message': _('You are not eligible to detach this item')})

        return super(DetachNodeView, self).dispatch(request, *args, **kwargs)


# class DetachNodeView2(LoginRequiredMixin, AjaxTemplateMixin, TemplateView):
#     template_name = "tree/detach_confirmation.html"
#
#     def get_context_data(self, **kwargs):
#         context = super(DetachNodeView2, self).get_context_data(**kwargs)
#         message_list = detach_node_service.detach_node(self.request.GET.get('path'), commit=False)
#         display_business_messages(self.request, message_list.messages)
#         context['detach_ok'] = not message_list.contains_errors()
#         context['confirmation_message'] = _("Are you sure you want to detach ?")
#         return context
#
#     def get_initial(self):
#         print()
#         return {
#             **super().get_initial(),
#             'path': self.request.GET.get('path')
#         }
#
#     def form_valid(self, form):
#         message_list = form.save()
#         display_business_messages(self.request, message_list.messages)
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return ""
