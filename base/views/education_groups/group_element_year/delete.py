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
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView

from base.business.group_element_years.detach import DetachEducationGroupYearStrategy, DetachLearningUnitYearStrategy
from base.models.exceptions import AuthorizedRelationshipNotRespectedException
from base.views.common import display_error_messages, display_success_messages
from base.views.education_groups.group_element_year import perms as group_element_year_perms
from base.views.education_groups.group_element_year.common import GenericGroupElementYearMixin


class DetachGroupElementYearView(GenericGroupElementYearMixin, DeleteView):
    # DeleteView
    template_name = "education_group/group_element_year/confirm_detach_inner.html"

    rules = [group_element_year_perms.can_update_group_element_year]

    def _call_rule(self, rule):
        return rule(self.request.user, self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self._check_if_deletable(self.object):
            context['confirmation_message'] = _("Are you sure you want to detach %(acronym)s ?") % {
                "acronym": self.object.child.acronym
            }

        return context

    def _check_if_deletable(self, obj):
        """
        The use cannot delete the object if :
            - the child has or is prerequisite
            - the minimum of children is reached
            - try to remove option (2m) which are present in one of its finality

        In that case, a message will be display in the modal to block the post action.
        """
        error_msg = None
        try:
            strategy = DetachEducationGroupYearStrategy if obj.child_branch else DetachLearningUnitYearStrategy
            strategy(obj).is_valid()
        except AuthorizedRelationshipNotRespectedException as e:
            error_msg = e.errors
        except ValidationError as e:
            error_msg = e.messages

        if error_msg:
            display_error_messages(self.request, error_msg)
            return False
        return True

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self._check_if_deletable(obj):
            return JsonResponse({"error": True})

        success_msg = _("\"%(child)s\" has been detached from \"%(parent)s\"") % {
            'child': obj.child,
            'parent': obj.parent,
        }
        display_success_messages(request, success_msg)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        # We can just reload the page
        return
