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

from program_management.ddd.domain.program_tree import ProgramTree
from program_management.ddd.service import attach_node_service
from program_management.models.enums.node_type import NodeType
from program_management.ddd.repositories import fetch_node


class AttachNodeForm(forms.Form):
    node_id = forms.IntegerField(widget=forms.HiddenInput)
    node_type = forms.ChoiceField(choices=NodeType.choices())
    to_path = forms.CharField(widget=forms.HiddenInput)

    def save(self):
        node = fetch_node.fetch_by_type(self.cleaned_data['node_type'], self.cleaned_data['node_id'])

        root_id, _ = self.cleaned_data['to_path'].split('|', 1)
        tree = ProgramTree(root_id)
        attach_node_service.attach_node(
            tree,
            node,
            self.cleaned_data.pop('to_path'),
            # **self.cleaned_data
        )
