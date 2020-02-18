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
from django.utils.translation import ngettext

from base.models.enums.education_group_types import TrainingType
from program_management.ddd.contrib.validation import BusinessValidator
from program_management.ddd.domain.program_tree import ProgramTree


class AttachFinalityEndDateValidator(BusinessValidator):
    """
    In context of 2M, when we add a finality [or group which contains finality], we must ensure that
    the end date of all 2M is greater or equals of all finalities.
    """

    def __init__(self, tree: ProgramTree, tree_from_node_to_add: ProgramTree, *args):
        super(AttachFinalityEndDateValidator, self).__init__()
        msg = "This validator need the children of the node to add. Please fetch the complete Tree from the Node to Add"
        assert isinstance(tree_from_node_to_add, ProgramTree), msg  # TODO :: déplacer les asserts dans le validate() -> c'est une validation métier ? (ce qui signifie qu'on ne pourrait pas faire de déplacement d'options en dehors du contexte 2M)
        self.node_to_add = tree_from_node_to_add.root_node
        if self._get_all_finality_nodes():
            assert_error_msg = "To use correctly this validator, make sure the ProgramTree root is of type 2M"
            assert tree.root_node.node_type in TrainingType.root_master_2m_types_enum(), assert_error_msg
        self.tree = tree

    def validate(self):
        if self._get_all_finality_nodes():
            inconsistent_nodes = self._get_acronyms_where_end_date_gte_root_end_date()
            if inconsistent_nodes:
                self.add_error_message(
                    ngettext(
                        "Finality \"%(acronym)s\" has an end date greater than %(root_acronym)s program.",
                        "Finalities \"%(acronym)s\" have an end date greater than %(root_acronym)s program.",
                        len(inconsistent_nodes)
                    ) % {
                        "acronym": ', '.join(inconsistent_nodes),
                        "root_acronym": self.tree.root_node.acronym
                    }
                )

    def _get_all_finality_nodes(self):  # TODO :: déplacer dans ProgramTree en tant qu'attr ?
        all_finalities = set()
        finality_types = set(TrainingType.finality_types_enum())
        if self.node_to_add.node_type in finality_types:
            all_finalities.add(self.node_to_add)
        return all_finalities | self.node_to_add.get_all_children_as_nodes(filter_types=finality_types)

    def _get_acronyms_where_end_date_gte_root_end_date(self):
        return [
            finality.acronym for finality in self._get_all_finality_nodes()
            if finality.end_date > self.tree.root_node.end_date
        ]
