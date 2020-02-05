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
from program_management.ddd.contrib.validation import BusinessListValidator
from program_management.ddd.domain.node import NodeEducationGroupYear, NodeLearningUnitYear, Node, \
    NodeGroupYear
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.ddd.validators.attach_finality_end_date_validator import \
    AttachFinalityEndDateValidator
from program_management.ddd.validators.attach_option_validator import AttachOptionsValidator
from program_management.ddd.validators.authorized_relationship_validator import \
    AuthorizedRelationshipValidator, AuthorizedRelationshipLearningUnitValidator
from program_management.ddd.validators.minimum_editable_year_validator import \
    MinimumEditableYearValidator
from program_management.ddd.validators.node_duplication_validator import NodeDuplicationValidator
from program_management.ddd.validators.parent_leaf_forbidden_validator import ParentIsNotLeafValidator


class AttachNodeValidatorList(BusinessListValidator):

    def __init__(self, tree: ProgramTree, node_to_add: Node, path: str):

        if isinstance(node_to_add, NodeEducationGroupYear) or isinstance(node_to_add, NodeGroupYear):

            self.validators = [
                ParentIsNotLeafValidator,
                AuthorizedRelationshipValidator,
                AttachOptionsValidator,
                AttachFinalityEndDateValidator,
                NodeDuplicationValidator,
                MinimumEditableYearValidator,
            ]

        elif isinstance(node_to_add, NodeLearningUnitYear):

            self.validators = [
                ParentIsNotLeafValidator,
                AuthorizedRelationshipLearningUnitValidator,
                NodeDuplicationValidator,
                MinimumEditableYearValidator,
            ]

        else:
            raise AttributeError("Unknown instance of node")

        super(AttachNodeValidatorList, self).__init__(validator_args=[tree, node_to_add, path])
