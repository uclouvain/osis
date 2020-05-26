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

from base.ddd.utils.business_validator import BusinessValidator
from program_management.ddd.repositories import load_tree
from program_management.ddd.validators._attach_finality_end_date import AttachFinalityEndDateValidator
from program_management.ddd.validators._attach_option import AttachOptionsValidator
from program_management.ddd.business_types import *


class ValidateEndDateAndOptionFinality(BusinessValidator):
    def __init__(self, node_to_paste: 'Node'):
        super().__init__()
        self.node_to_paste = node_to_paste

    def validate(self, *args, **kwargs):
        tree = load_tree.load(self.node_to_paste.node_id)
        finality_ids = [n.node_id for n in tree.get_all_finalities()]
        if self.node_to_paste.is_finality() or finality_ids:
            trees_2m = [
                tree for tree in load_tree.load_trees_from_children(child_branch_ids=finality_ids)
                if tree.is_master_2m()
            ]
            for tree_2m in trees_2m:
                validator = AttachFinalityEndDateValidator(tree_2m, tree)
                if not validator.is_valid():
                    for msg in validator.error_messages:
                        self.add_error_message(msg.message)
                validator = AttachOptionsValidator(tree_2m, tree)
                if not validator.is_valid():
                    for msg in validator.error_messages:
                        self.add_error_message(msg.message)
