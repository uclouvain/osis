##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.models.prerequisite import Prerequisite
from program_management.ddd.validators._authorized_root_type_for_prerequisite import AuthorizedRootTypeForPrerequisite
from program_management.forms.prerequisite import LearningUnitPrerequisiteForm
from program_management.views.generic import LearningUnitGenericUpdateView


class LearningUnitPrerequisite(LearningUnitGenericUpdateView):
    template_name = "learning_unit/tab_prerequisite_update.html"
    form_class = LearningUnitPrerequisiteForm  # TODO Update form to use ddd domain objects

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        try:
            instance = Prerequisite.objects.get(education_group_year=self.kwargs["root_id"],
                                                learning_unit_year=self.kwargs["learning_unit_year_id"])
        except Prerequisite.DoesNotExist:
            instance = Prerequisite(
                education_group_year=self.get_root(),
                learning_unit_year=self.object
            )
        form_kwargs["instance"] = instance
        form_kwargs["codes_permitted"] = self.program_tree.get_codes_permitted_as_prerequisite()
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["show_prerequisites"] = True

        self.check_can_update_prerequisite()

        return context

    #  FIXME refactor permission with new permission module
    def check_can_update_prerequisite(self):
        validator = AuthorizedRootTypeForPrerequisite(self.program_tree.root_node)
        if not validator.is_valid():
            raise PermissionDenied(
                [msg.message for msg in validator.error_messages]
            )

    def get_success_message(self, cleaned_data):
        return _("Prerequisites saved.")

    def get_success_url(self):
        return reverse("learning_unit_prerequisite", args=[self.kwargs["root_id"],
                                                           self.kwargs["learning_unit_year_id"]])
