# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from typing import List

from base.models.enums.link_type import LinkTypes
from program_management.ddd.repositories import load_tree
from program_management.ddd.validators._authorized_relationship import PasteAuthorizedRelationshipValidator
from program_management.ddd.business_types import *


def __validate_trees_using_node_as_reference_link(
        tree: 'ProgramTree',
        node_to_attach: 'Node',
        path: 'Path'
) -> List['BusinessValidationMessage']:

    error_messages = []
    child_node = tree.get_node(path)
    trees = load_tree.load_trees_from_children([child_node.node_id], link_type=LinkTypes.REFERENCE)
    for tree in trees:
        for parent_from_reference_link in tree.get_parents_using_node_as_reference(child_node):
            validator = PasteAuthorizedRelationshipValidator(tree, node_to_attach, parent_from_reference_link)
            if not validator.is_valid():
                error_messages += validator.error_messages
    return error_messages
