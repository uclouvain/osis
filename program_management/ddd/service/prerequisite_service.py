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
from typing import List

from base.ddd.utils.validation_message import BusinessValidationMessageList
from program_management.ddd.business_types import *
from program_management.ddd.service.tree_service import search_trees_using_node
from program_management.ddd.validators._has_or_is_prerequisite import IsPrerequisiteValidator


def check_is_prerequisite_in_trees_using_node(
        node_to_detach: 'Node',
        trees_using_node: List['ProgramTree'] = None
) -> BusinessValidationMessageList:
    if trees_using_node is None:
        trees_using_node = search_trees_using_node(node_to_detach)
    messages = []
    for tree in trees_using_node:
        validator = IsPrerequisiteValidator(tree, node_to_detach)
        if not validator.is_valid():
            messages += validator.messages
    return BusinessValidationMessageList(messages=messages)
