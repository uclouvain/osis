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

from django.utils.translation import gettext_lazy as _

import program_management.ddd.command
from program_management.ddd.business_types import *
from program_management.ddd.repositories import load_tree, load_node
from program_management.ddd.validators._validate_end_date_and_option_finality import \
    _validate_end_date_and_option_finality
from program_management.ddd.validators import link as link_validator, _minimum_editable_year, _infinite_recursivity


# FIXME Pass repository to method attach_node and move validations inside AttachNodeValidatorList


def check_attach(check_command: program_management.ddd.command.CheckAttachNodeCommand) -> List['BusinessValidationMessage']:
    tree_root_id = check_command.root_id
    path_of_node_to_attach_from = check_command.path_where_to_attach
    nodes_to_attach = check_command.nodes_to_attach
    result = []
    tree = load_tree.load(tree_root_id)
    node_to_attach_from = tree.get_node(path_of_node_to_attach_from)

    _nodes_to_attach = [load_node.load_by_type(node_type, node_id) for node_id, node_type in nodes_to_attach]

    if not _nodes_to_attach:
        result.append(
            _("Please select an item before adding it")
        )

    for node_to_attach in _nodes_to_attach:
        if not node_to_attach.is_learning_unit():
            result.extend(_validate_end_date_and_option_finality(node_to_attach))

        validator = link_validator.CreateLinkValidatorList(node_to_attach_from, node_to_attach)
        if not validator.is_valid():
            result.extend(validator.messages)

        validator = _minimum_editable_year.MinimumEditableYearValidator(tree)
        if not validator.is_valid():
            result.extend(validator.messages)

        validator = _infinite_recursivity.InfiniteRecursivityTreeValidator(
            tree,
            node_to_attach,
            path_of_node_to_attach_from
        )
        if not validator.is_valid():
            result.extend(validator.messages)

    return result


