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
from program_management.DomainDrivenDesign.contrib.validation import BusinessListValidator
from program_management.DomainDrivenDesign.domain.node import NodeEducationGroupYear, NodeLearningUnitYear, Node, \
    NodeGroupYear
from program_management.DomainDrivenDesign.domain.program_tree import ProgramTree
from program_management.DomainDrivenDesign.validators.attach_finality_end_date_validator import \
    AttachFinalityEndDateValidator
from program_management.DomainDrivenDesign.validators.attach_option_validator import AttachOptionsValidator
from program_management.DomainDrivenDesign.validators.authorized_relationship_validator import \
    AuthorizedRelationshipValidator, AuthorizedRelationshipLearningUnitValidator
from program_management.DomainDrivenDesign.validators.minimum_editable_year_validator import \
    MinimumEditableYearValidator
from program_management.DomainDrivenDesign.validators.node_duplication_validator import NodeDuplicationValidator
from program_management.DomainDrivenDesign.validators.parent_leaf_forbidden_validator import ParentIsNotLeafValidator


class AttachGroupYearNodeValidator(BusinessListValidator):
    validators = [
        ParentIsNotLeafValidator,
        AuthorizedRelationshipValidator,
        AttachOptionsValidator,
        AttachFinalityEndDateValidator,
        NodeDuplicationValidator,
        MinimumEditableYearValidator,
    ]


class AttachLearningUnitYearNodeValidator(BusinessListValidator):
    validators = [
        ParentIsNotLeafValidator,
        AuthorizedRelationshipLearningUnitValidator,
        NodeDuplicationValidator,
        MinimumEditableYearValidator,
    ]


class AttachNodeValidatorFactory:
    def get_attach_node_validator(self, tree: ProgramTree, node_to_add: Node, where_to_add: str):
        if isinstance(node_to_add, NodeEducationGroupYear) or isinstance(node_to_add, NodeGroupYear):
            attach_node_validator_class = AttachGroupYearNodeValidator
        elif isinstance(node_to_add, NodeLearningUnitYear):
            attach_node_validator_class = AttachLearningUnitYearNodeValidator
        else:
            raise AttributeError("Unknown instance of node")
        return attach_node_validator_class(validator_args=[tree, node_to_add, where_to_add])


factory = AttachNodeValidatorFactory()
