############################################################################
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
############################################################################
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView

from base.business.group_element_years.management import is_min_child_reached
from base.views.common import display_error_messages, display_success_messages
from base.views.education_groups.group_element_year.common import GenericGroupElementYearMixin


class DetachGroupElementYearView(GenericGroupElementYearMixin, DeleteView):
    # DeleteView
    template_name = "education_group/group_element_year/confirm_detach_inner.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._check_if_deletable(self.object)
        return context

    def _check_if_deletable(self, obj):
        child_leaf = obj.child_leaf
        child_branch = obj.child_branch
        error_msg = ""
        if child_leaf and child_leaf.has_or_is_prerequisite(obj.parent):
            error_msg = \
                _("Cannot detach learning unit %(acronym)s as it has a prerequisite or it is a prerequisite.") % {
                    "acronym": child_leaf.acronym
                }
        if child_branch and is_min_child_reached(obj.parent, child_branch.education_group_type):
            error_msg = \
                _("Cannot detach child \"%(child)s\". "
                  "The parent must have at least one child of type \"%(type)s\".") % {
                    "child": child_branch,
                    "type": child_branch.education_group_type
                }

        if error_msg:
            display_error_messages(self.request, error_msg)
            return False
        return True

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self._check_if_deletable(obj):
            return JsonResponse({"error": True, "success_url": self.get_success_url()})

        success_msg = _("\"%(child)s\" has been detached from \"%(parent)s\"") % {
            'child': obj.child,
            'parent': obj.parent,
        }
        display_success_messages(request, success_msg)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        # We can just reload the page
        return
