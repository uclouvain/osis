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

from django.db import transaction

from education_group.ddd.service.write import create_group_service
from program_management.ddd import command
from program_management.ddd.domain.program_tree import ProgramTreeBuilder, ProgramTreeIdentity
from program_management.ddd.domain.service.validation_rule import FieldValidationRule
from program_management.ddd.repositories.program_tree import ProgramTreeRepository


@transaction.atomic()
def duplicate_program_tree(
        cmd: command.DuplicateProgramTree
) -> 'ProgramTreeIdentity':
    # GIVEN
    program_tree_identity = ProgramTreeIdentity(code=cmd.from_root_code, year=cmd.from_root_year)
    existing_tree = ProgramTreeRepository().get(entity_id=program_tree_identity)

    # WHEN
    program_tree = ProgramTreeBuilder().duplicate(
        duplicate_from=existing_tree,
        override_end_year_to=cmd.override_end_year_to,
        override_start_year_to=cmd.override_start_year_to
    )
    validation_rule_credits = FieldValidationRule.get(
        program_tree.root_node.node_type, 'credits', is_version=True
    )
    validation_rule_contraint_type = FieldValidationRule.get(
        program_tree.root_node.node_type, 'constraint_type', is_version=True
    )
    validation_rule_min_constraint = FieldValidationRule.get(
        program_tree.root_node.node_type, 'min_constraint', is_version=True
    )
    validation_rule_max_constraint = FieldValidationRule.get(
        program_tree.root_node.node_type, 'max_constraint', is_version=True
    )
    validation_rule_remark_fr = FieldValidationRule.get(
        program_tree.root_node.node_type, 'remark_fr', is_version=True
    )
    validation_rule_remark_en = FieldValidationRule.get(
        program_tree.root_node.node_type, 'remark_en', is_version=True
    )
    program_tree.root_node.credits = validation_rule_credits.initial_value or None
    program_tree.root_node.constraint_type = validation_rule_contraint_type.initial_value or None
    program_tree.root_node.min_constraint = validation_rule_min_constraint.initial_value or None
    program_tree.root_node.max_constraint = validation_rule_max_constraint.initial_value or None
    program_tree.root_node.remark_fr = validation_rule_remark_fr.initial_value
    program_tree.root_node.remark_en = validation_rule_remark_en.initial_value
    # THEN
    program_tree_identity = ProgramTreeRepository().create(
        program_tree=program_tree,
        create_orphan_group_service=create_group_service.create_orphan_group
    )

    return program_tree_identity
