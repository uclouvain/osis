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
from program_management.contrib.validation import BusinessValidator, BusinessListValidator
from program_management.domain import node
from program_management.domain.program_tree import ProgramTree


# class AttachNodeValidator(BusinessValidator):
#     # tree: ProgramTree = None
#     # node_to_add: node.Node = None
#     # where_to_add: str = None
#     #
#     # def __init__(self, tree: ProgramTree, node_to_add: node.Node, where_to_add: str):
#     #     super(AttachNodeValidator, self).__init__()
#     #     self.tree = tree
#     #     self.node_to_add = node_to_add
#     #     self.where_to_add = where_to_add
#
#     def validate(self, tree: ProgramTree, node_to_add: node.Node, where_to_add: str):
#         raise NotImplementedError()


class AuthorizedRelationshipValidator(BusinessValidator):
    # TODO :: comment gérer l'utilisation de ces données? (Business ne peut pas faire appel à modèle)
    def validate(self):
        pass  # Implements rules based on AuthorizedRelationhips


class AttachOptionsValidator(BusinessValidator):
    def validate(self):
            pass  # cf. _check_attach_options_rules


class AttachFinalityEndDateValidator(BusinessValidator):
    def validate(self):
        pass  # cf. _check_end_year_constraints_on_2m


class NodeDuplicationValidator(BusinessValidator):
    def validate(self):
        pass  # cf. _check_new_attach_is_not_duplication


class ParentIsNotLeafValidator(BusinessValidator):
    def validate(self):
        pass  # cf. AttachPermission._check_if_leaf


class MinimumEditableYearValidator(BusinessValidator):
    def validate(self):
        pass  # cf. AttachPermission._check_year_is_editable


class AuthorizedRelationshipLearningUnitValidator(BusinessValidator):
    def validate(self):
        pass  # cf. AttachLearningUnitYearStrategy.id_valid


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
    def get_attach_node_validator(self, tree: ProgramTree, node_to_add: node.Node, where_to_add: str):
        if isinstance(node_to_add, node.NodeEducationGroupYear) or isinstance(node_to_add, node.NodeGroupYear):
            attach_node_validator_class = AttachGroupYearNodeValidator
        elif isinstance(node_to_add, node.NodeLearningUnitYear):
            attach_node_validator_class = AttachLearningUnitYearNodeValidator
        else:
            raise AttributeError("Unknown instance of node")
        return attach_node_validator_class(validator_args=[tree, node_to_add, where_to_add])


factory = AttachNodeValidatorFactory()
