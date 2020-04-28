from typing import Optional

from django.utils.translation import gettext as _

from base.ddd.utils.business_validator import BusinessListValidator
from base.models.enums.link_type import LinkTypes
from program_management.ddd.business_types import *
from program_management.ddd.validators._authorized_link_type import AuthorizedLinkTypeValidator
from program_management.ddd.validators._infinite_recursivity import InfiniteRecursivityLinkValidator
from program_management.ddd.validators._node_duplication import NodeDuplicationValidator
from program_management.ddd.validators._parent_as_leaf import ParentIsNotLeafValidator
from program_management.ddd.validators._parent_child_academic_year import ParentChildSameAcademicYearValidator


class CreateLinkValidatorList(BusinessListValidator):
    success_messages = [
        _('Success message')
    ]

    def __init__(self, parent_node: 'Node', node_to_add: 'Node', link_type: Optional[LinkTypes]):
        self.validators = [
            ParentIsNotLeafValidator(parent_node, node_to_add),
            NodeDuplicationValidator(parent_node, node_to_add),
            ParentChildSameAcademicYearValidator(parent_node, node_to_add),
            InfiniteRecursivityLinkValidator(parent_node, node_to_add),
            AuthorizedLinkTypeValidator(parent_node, node_to_add, link_type)
        ]
        super().__init__()
