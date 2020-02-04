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

from program_management.DomainDrivenDesign.domain.program_tree import ProgramTree
from program_management.models.enums import node_type
from program_management.DomainDrivenDesign.repositories import fetch_node


class AttachNodeForm(forms.Form):
    node_id = forms.IntegerField(widget=forms.HiddenInput)
    to_path = forms.CharField(widget=forms.HiddenInput)

    def save(self):
        root_id, _ = self.cleaned_data['to_path'].split('|', 1)
        # According to cache class
        node = fetch_node.fetch_by_type(node_type.EDUCATION_GROUP, self.cleaned_data['node_id'])

        tree = ProgramTree(root_id)
        tree.attach_node(
            node,
            path=self.cleaned_data.pop('to_path'),
            **self.cleaned_data
        )
