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
from program_management.ddd.contrib.validation import BusinessValidator
from program_management.ddd.domain import node
from program_management.ddd.domain.program_tree import ProgramTree
from django.utils.translation import gettext as _


class AuthorizedRelationshipValidator(BusinessValidator):

    tree = None
    node_to_add = None
    parent = None

    def __init__(self, tree: ProgramTree, node_to_add: node.Node, path: str):
        super(AuthorizedRelationshipValidator, self).__init__()
        self.tree = tree
        self.node_to_add = node_to_add
        self.parent = tree.get_node(path)

    def validate(self):
        if not self.tree.authorized_relationships.is_authorized(self.parent, self.node_to_add):
            self.add_error_message(
                _("You cannot add \"%(child_types)s\" to \"%(parent)s\" (type \"%(parent_type)s\")") % {
                    'child_types': self.node_to_add.node_type.value,
                    'parent': self.parent,
                    'parent_type': self.parent.node_type.value,
                }
            )


# TODO :: ne pas hériter de la classe? Et lister AttachAuthorizedRelationshipValidator + AuthorizedRelationshipValidator dans le BusinessListVaidator?
class AttachAuthorizedRelationshipValidator(AuthorizedRelationshipValidator):
    def validate(self):
        super(AttachAuthorizedRelationshipValidator, self).validate()
        if self.tree.authorized_relationships.is_maximum_children_types_reached(self.parent, self.node_to_add):
            self.add_error_message(
                _("The parent must have at least one child of type(s) \"%(types)s\".") % {
                    "types": str(self.tree.authorized_relationships.get_authorized_children_types(self.parent))
                }
            )


class DetachAuthorizedRelationshipValidator(AuthorizedRelationshipValidator):
    def validate(self):
        super(DetachAuthorizedRelationshipValidator, self).validate()
        if self.tree.authorized_relationships.is_minimum_children_types_reached(self.parent, self.node_to_add):
            self.add_error_message(
                _("The number of children of type(s) \"%(child_types)s\" for \"%(parent)s\" "
                  "has already reached the limit.") % {
                    'child_types': self.node_to_add.node_type.value,
                    'parent': self.parent
                }
            )


class AuthorizedRelationshipLearningUnitValidator(BusinessValidator):
    def validate(self):
        pass  # cf. AttachLearningUnitYearStrategy.id_valid
