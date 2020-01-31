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
from program_management.contrib.validation import BusinessValidator, BusinessListValidator, BusinessValidationMessage
from program_management.domain import node
from program_management.domain.program_tree import ProgramTree
from django.utils.translation import gettext as _
from program_management.domain.authorized_relationship import AuthorizedRelationshipList


#  TODO :: unit tests on validation
class AuthorizedRelationshipValidator(BusinessValidator):

    tree: ProgramTree = None
    node_to_add: node.Node = None
    parent: node.Node = None
    authorized_relationships: AuthorizedRelationshipList = None

    def __init__(
            self,
            tree: ProgramTree,
            node_to_add: node.Node,
            path: str,
            authorized_relationships: AuthorizedRelationshipList = None
    ):
        super(AuthorizedRelationshipValidator, self).__init__()
        self.tree = tree
        self.node_to_add = node_to_add
        self.parent = tree.get_node(path)
        self.authorized_relationships = authorized_relationships

    def validate(self):
        if self.authorized_relationships.is_minimum_children_types_reached(self.parent, self.node_to_add):
            self.add_error_message(
                _("The number of children of type(s) \"%(child_types)s\" for \"%(parent)s\" "
                  "has already reached the limit.") % {
                    'child_types': self.node_to_add.node_type.value,
                    'parent': self.parent
                }
            )

        if self.authorized_relationships.is_maximum_children_types_reached(self.parent, self.node_to_add):
            self.add_error_message(
                _("The parent must have at least one child of type(s) \"%(types)s\".") % {
                    "types": ', '.join(self.authorized_relationships.get_authorized_children_types(self.parent))
                }
            )

        if not self.authorized_relationships.is_authorized(self.parent, self.node_to_add):
            self.add_error_message(
                _("You cannot add \"%(child_types)s\" to \"%(parent)s\" (type \"%(parent_type)s\")") % {
                    'child_types': self.node_to_add,
                    'parent': self.parent,
                    'parent_type': self.parent.node_type.value,
                }
            )


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
