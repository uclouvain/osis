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
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from program_management.ddd.domain import program_tree, node
from program_management.ddd.service import detach_node_service


class DetachNodeForm(forms.Form):
    path = forms.CharField(widget=forms.HiddenInput)

    _warnings = None

    _business_messages = None

    # def __init__(self, **kwargs):
    # self.path_to_detach = path_to_detach
    # super().__init__(**kwargs)

    # def clean_path(self):
    #     path = self.cleaned_data['path']
    #     try:
    #         self.tree.get_node(path)
    #     except node.NodeNotFoundException:
    #         raise forms.ValidationError(_("Invalid tree path"))
    #     return path

    @property
    def confirmation_message(self):
        return _("Are you sure you want to detach ?")

    # def is_valid(self):
    #     is_valid = super(DetachNodeForm, self).is_valid()
    #     if not is_valid:
    #         return is_valid
    #
    #     message_list = detach_node_service.detach_node(self.cleaned_data['path'], commit=False)
    #     self._business_messages = message_list.messages
    #     serialized_messages = business_messages_serializer(message_list.messages)
    #
    #     if message_list.contains_errors():
    #         raise ValidationError(serialized_messages['error'])
    #     # raise ValidationError(_('error message test'))
    #
    #     self._warnings = serialized_messages['warnings']
    #
    #     return True

    @property
    def business_messages(self):
        if self._business_messages is None:
            self._business_messages = []
        return self._business_messages
    # @property
    # def warnings(self):
    #     if self._warnings is None:
    #         self._warnings = []
    #     return [_('Warning message test')]

    def save(self):
        return detach_node_service.detach_node(self.cleaned_data['path'])
