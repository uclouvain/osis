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

from base.ddd.utils.business_validator import BusinessValidator
from base.models.enums.education_group_types import MiniTrainingType, TrainingType
from program_management.ddd.business_types import *


class AttachOptionsValidator(BusinessValidator):
    """
    In context of MA/MD/MS when we add an option [or group which contains options],
    this options must exist in parent context (2m)
    """

    def __init__(self, tree_2m: 'ProgramTree', tree_from_node_to_add: 'ProgramTree', *args):
        super(AttachOptionsValidator, self).__init__()
        if tree_from_node_to_add.root_node.is_finality() or tree_from_node_to_add.get_all_finalities():
            assert_error_msg = "To use correctly this validator, make sure the ProgramTree root is of type 2M"
            assert tree_2m.root_node.node_type in TrainingType.root_master_2m_types_enum(), assert_error_msg
        self.tree_from_node_to_add = tree_from_node_to_add
        self.node_to_add = tree_from_node_to_add.root_node
        self.tree_2m = tree_2m

    def get_options_to_attach(self):
        options = self.tree_from_node_to_add.root_node.get_all_children_as_nodes(take_only={MiniTrainingType.OPTION})
        if self.node_to_add.is_option():
            options.add(self.tree_from_node_to_add.root_node)
        return options

    def validate(self):
        options_to_attach = self.get_options_to_attach()
        if options_to_attach:
            options_from_2m_option_list = self.tree_2m.get_2m_option_list()
            options_to_attach_not_present_in_2m_option_list = options_to_attach - options_from_2m_option_list
            if options_to_attach_not_present_in_2m_option_list:
                self.add_error_message(
                    ngettext(
                        "Option \"%(code)s\" must be present in %(root_code)s program.",
                        "Options \"%(code)s\" must be present in %(root_code)s program.",
                        len(options_to_attach_not_present_in_2m_option_list)
                    ) % {
                        "code": ', '.join(option.code for option in options_to_attach_not_present_in_2m_option_list),
                        "root_code": self.tree_2m.root_node.code
                    }
                )
