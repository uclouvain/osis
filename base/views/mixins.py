##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import waffle
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView

from base.views import common


class FlagMixin:
    flag = None

    def dispatch(self, request, *args, **kwargs):
        if self.flag and not waffle.flag_is_active(request, self.flag):
            raise Http404
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class RulesRequiredMixin(UserPassesTestMixin):
    """CBV mixin extends the permission_required with rules on objects """
    rules = []

    def test_func(self):
        if not self.rules:
            return True

        try:
            # Requires SingleObjectMixin or equivalent ``get_object`` method
            return all(self._call_rule(rule) for rule in self.rules)

        except PermissionDenied as e:
            # The rules can override the default message
            self.permission_denied_message = str(e)
            return False

    def _call_rule(self, rule):
        """ The signature can be override with another object """
        return rule(self.request.user, self.get_object())


class AjaxTemplateMixin:
    ajax_template_suffix = "_inner"

    def get_template_names(self):
        template_names = super().get_template_names()
        if self.request.is_ajax():
            template_names = [
                self._convert_template_name_to_ajax_template_name(template_name) for template_name in template_names
            ]
        return template_names

    def _convert_template_name_to_ajax_template_name(self, template_name):
        if "_inner.html" not in template_name:
            split = template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            return "".join(split)
        return template_name

    def form_valid(self, form):
        redirect = super().form_valid(form)

        # When the form is saved, we return only the url, not all the template
        if self.request.is_ajax():
            return JsonResponse({"success": True, "success_url": self.get_success_url()})
        else:
            return redirect

    def delete(self, request, *args, **kwargs):
        redirect = super().delete(request, *args, **kwargs)

        # When the form is saved, we return only the url, not all the template
        if self.request.is_ajax():
            return JsonResponse({"success": True, "success_url": self.get_success_url()})
        else:
            return redirect


class DeleteViewWithDependencies(FlagMixin, RulesRequiredMixin, AjaxTemplateMixin, DeleteView):
    success_message = "The objects are been deleted successfully"
    protected_template = None
    protected_messages = None

    def get(self, request, *args, **kwargs):
        self.protected_messages = self.get_protected_messages()

        # If there is some protected messages, change the template
        if self.protected_messages:
            self.template_name = self.protected_template
        return super().get(request, *args, **kwargs)

    def get_protected_messages(self):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["protected_messages"] = self.protected_messages
        return context

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        common.display_success_messages(request, _(self.success_message))
        return result
