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
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView

from base.business import group_element_years
from base.views.common import display_error_messages, display_success_messages
from base.views.education_groups.group_element_year.common import GenericGroupElementYearMixin


class DetachGroupElementYearView(GenericGroupElementYearMixin, DeleteView):
    # DeleteView
    template_name = "education_group/group_element_year/confirm_detach_inner.html"

    def delete(self, request, *args, **kwargs):
        child_leaf = self.get_object().child_leaf
        child_branch = self.get_object().child_branch
        parent = self.get_object().parent
        if child_leaf and child_leaf.has_or_is_prerequisite(parent):
            # FIXME Method should be in permission to view and display message in page
            error_msg = \
                _("Cannot detach learning unit %(acronym)s as it has a prerequisite or it is a prerequisite.") % {
                    "acronym": child_leaf.acronym
                }
            display_error_messages(request, error_msg)
            return JsonResponse({"error": True, "success_url": self.get_success_url()})
        if child_branch and \
                group_element_years.management.is_min_child_reached(parent, child_branch.education_group_type):
            error_msg = \
                _("Cannot detach child \"%(child)s\". "
                  "The parent must have at least one child of type \"%(type)s\".") % {
                    "child": child_branch,
                    "type": child_branch.education_group_type
                }
            display_error_messages(request, error_msg)
            return JsonResponse({"error": True, "success_url": self.get_success_url()})

        success_msg = _("\"%(child)s\" has been detached from \"%(parent)s\"") % {
            'child': self.get_object().child,
            'parent': self.get_object().parent,
        }
        display_success_messages(request, success_msg)
        return super().delete(request, *args, **kwargs)

    def _call_rule(self, rule):
        """ The permission is computed from the parent education_group_year """
        return rule(self.request.user, self.get_object().parent)

    def get_success_url(self):
        return self.kwargs.get('http_referer')
