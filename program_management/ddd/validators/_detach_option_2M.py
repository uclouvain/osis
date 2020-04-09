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
from collections import Counter
from typing import List

from django.utils.translation import ngettext

from base.ddd.utils.business_validator import BusinessValidator
from base.models.enums.education_group_types import MiniTrainingType, TrainingType
from program_management.ddd.business_types import *
from program_management.ddd.domain import program_tree


# Implmented from _check_detach_options_rules
class DetachOptionValidator(BusinessValidator):
    """
    In context of MA/MD/MS when we add an option [or group which contains options],
    this options must exist in parent context (2m)
    """

    def __init__(self, working_tree: 'ProgramTree', path_to_node_to_detach: 'Path', trees_using_node: List['ProgramTree']):
        super(DetachOptionValidator, self).__init__()
        self.working_tree = working_tree
        self.path_to_node_to_detach = path_to_node_to_detach
        self.node_to_detach = working_tree.get_node(path_to_node_to_detach)
        self.trees_2m = [
            tree for tree in trees_using_node if tree.is_master_2m()
        ]
        for tree in self.trees_2m:
            assert tree.get_node_by_id_and_class(self.node_to_detach.node_id, self.node_to_detach.node_type)
        # msg = "This validator need the children of the node to add. Please load the complete Tree from the Node to Add"
        # assert isinstance(tree_from_node_to_add, program_tree.ProgramTree), msg
        # if tree_from_node_to_add.root_node.is_finality() or tree_from_node_to_add.get_all_finalities():
        #     assert_error_msg = "To use correctly this validator, make sure the ProgramTree root is of type 2M"
        #     assert tree_2m.root_node.node_type in TrainingType.root_master_2m_types_enum(), assert_error_msg
        # root_id = int(path_to_node_to_detach.split('|')[0])
        # self.working_tree = next(
        #     tree for tree in trees_containg_node
        #     if tree.root_node.node_id == root_id
        # )
        # self.tree_from_node_to_detach = ProgramTree(root_node=self.working_tree.get_node(path_to_node_to_detach))

    # def get_options_from_finality(self, finality: 'Node'):
    #     return finality.get_all_children_as_nodes(take_only={MiniTrainingType.OPTION})

    def get_options_to_detach(self):
        result = []
        if self.node_to_detach.is_option():
            result.append(self.node_to_detach)
        result += self.node_to_detach.get_option_list()
        return result

    # def get_trees_2m(self):
    #     return [tree for tree in self.trees_containing_node if tree.is_master_2m()]

    def validate(self):
        options_to_detach = self.get_options_to_detach()
        if options_to_detach:
            for tree_2m in self.trees_2m:
                counter_options = Counter(tree_2m.get_option_list())
                counter_options.subtract(options_to_detach)
                options_to_check = [opt for opt, count in counter_options.items() if count == 0]
                if not options_to_check:
                    continue
                for finality in tree_2m.get_all_finalities():
                    options_to_detach_used_in_finality = set(options_to_detach) & set(finality.get_option_list())
                    if options_to_detach_used_in_finality:
                        self.add_error_message(
                            ngettext(
                                "Option \"%(acronym)s\" cannot be detach because it is contained in"
                                " %(finality_acronym)s program.",
                                "Options \"%(acronym)s\" cannot be detach because they are contained in"
                                " %(finality_acronym)s program.",
                                len(options_to_detach_used_in_finality)
                            ) % {
                                "acronym": ', '.join(option.title for option in options_to_detach_used_in_finality),
                                "finality_acronym": finality.title
                            }
                        )

    # def is_options_to_detach_inside_2m(self):
    #     """
    #     :return:  False if the options to detach are inside a finality.
    #     True if not (in this case, we are inside the OPTION_LIST_CHOICE of 2M).
    #     """
    #     option_list_node_from_current_tree = self.working_tree.get_option_list_choice(self.path_to_node_to_detach)
    #     for tree in self.trees_2m:
    #         # Note : current working tree could be sth else than a 2M tree (e.g. Finality, OPTION_LIST_CHOICE...)
    #         # So, we need to retrieve the option_list_choice from the context of the 2M trees
    #         option_list_node_from_2m_tree = tree.get_node_by_id_and_class(
    #             option_list_node_from_current_tree.node_id,
    #             option_list_node_from_current_tree.node_type
    #         )
    #         if any(parent for parent in tree.get_parents_nodes(option_list_node_from_2m_tree) if parent.is_finality()):
    #             return False
    #     return True
