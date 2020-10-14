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
from typing import Iterable, Dict, List

from django.conf import settings
from django.utils.translation import gettext_lazy as _, ngettext

from osis_common.ddd.interface import BusinessException, BusinessExceptions
from program_management.ddd.business_types import *

BLOCK_MAX_AUTHORIZED_VALUE = 6


class RelativeCreditShouldBeGreaterOrEqualsThanZero(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Relative credits must be greater or equals than 0")
        super().__init__(message, **kwargs)


class RelativeCreditShouldBeLowerOrEqualThan999(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Relative credits must be lower or equals to 999")
        super().__init__(message, **kwargs)


class ProgramTreeNotFoundException(Exception):
    def __init__(self, *args, code: str = '', year: int = None):
        message = ''
        if code or year:
            message = _("Program tree not found : {code} {year}".format(code=code, year=year))
        super().__init__(message, *args)


class NodeNotFoundException(Exception):
    pass


class ProgramTreeVersionNotFoundException(Exception):
    pass


class ProgramTreeAlreadyExistsException(Exception):
    pass


class ProgramTreeNonEmpty(BusinessException):
    def __init__(self, program_tree: 'ProgramTree', **kwargs):
        message = _("[%(academic_year)s] The content of the program is not empty.") % {
                    'academic_year': program_tree.root_node.academic_year,
                }
        super().__init__(message, **kwargs)


class NodeHaveLinkException(BusinessException):
    def __init__(self, node: 'Node', **kwargs):
        message = _("[%(academic_year)s] %(code)s has links to another training / mini-training / group") % {
                    'academic_year': node.academic_year,
                    'code': node.code
                }
        super().__init__(message, **kwargs)


class CannotCopyTreeVersionDueToEndDate(BusinessException):
    def __init__(self, tree_version: 'ProgramTreeVersion', *args, **kwargs):
        message = _(
            "You can't copy the program tree version '{acronym}' "
            "from {from_year} to {to_year} because it ends in {end_year}"
        ).format(
            acronym=tree_version.entity_id.offer_acronym,
            from_year=tree_version.get_tree().root_node.year,
            to_year=tree_version.get_tree().root_node.year + 1,
            end_year=tree_version.get_tree().root_node.end_year,
        )
        super().__init__(message, **kwargs)


class CannotCopyTreeDueToEndDate(BusinessException):
    def __init__(self, tree: 'ProgramTree', *args, **kwargs):
        message = _(
            "You can't copy the program tree '{code}' "
            "from {from_year} to {to_year} because it ends in {end_year}"
        ).format(
            code=tree.entity_id.code,
            from_year=tree.root_node.year,
            to_year=tree.root_node.year + 1,
            end_year=tree.root_node.end_year,
        )
        super().__init__(message, **kwargs)


class CannotDeleteStandardDueToVersionEndDate(BusinessException):
    def __init__(self, tree: 'ProgramTreeVersion', *args, **kwargs):
        message = _(
            "You can't delete the standard program tree '{code}' "
            "in {year} as specific versions exists during this year."
        ).format(
            code=tree.program_tree_identity.code,
            year=tree.entity_id.year,
        )
        super().__init__(message, **kwargs)


class NodeIsUsedException(Exception):
    pass


class ProgramTreeVersionMismatch(BusinessExceptions):
    def __init__(
            self,
            node_to_add: 'Node',
            child_version_identity: 'ProgramTreeVersionIdentity',
            node_to_paste_to: 'Node',
            parents_version_mismatched_identity: List['ProgramTreeVersionIdentity'],
            *args,
            **kwargs
    ):
        parents_version_names = {
            self._get_version_name(version_identity) for version_identity in parents_version_mismatched_identity
        }
        messages = [_(
            "%(node_to_add)s version must be the same as %(node_to_paste_to)s "
            "and all of it's parent's version [%(version_mismatched)s]"
        ) % {
            'node_to_add': str(node_to_add),
            'node_to_add_version': self._get_version_name(child_version_identity),
            'node_to_paste_to': str(node_to_paste_to),
            'version_mismatched': ",".join(parents_version_names)
        }]
        super().__init__(messages, **kwargs)

    def _get_version_name(self, version_identity: 'ProgramTreeVersionIdentity'):
        return str(_('Standard')) if version_identity.is_standard() else version_identity.version_name


class Program2MEndDateShouldBeGreaterOrEqualThanItsFinalities(BusinessException):
    def __init__(self, finality: 'Node', **kwargs):
        message = _("The end date must be higher or equal to finality %(acronym)s") % {
            "acronym": str(finality)
        }
        super().__init__(message, **kwargs)


class CannotAttachFinalitiesWithGreaterEndDateThanProgram2M(BusinessException):
    def __init__(self, root_node: 'Node', finalities: List['Node']):
        message = ngettext(
            "Finality \"%(acronym)s\" has an end date greater than %(root_acronym)s program.",
            "Finalities \"%(acronym)s\" have an end date greater than %(root_acronym)s program.",
            len(finalities)
        ) % {
            "acronym": ', '.join([str(node) for node in finalities]),
            "root_acronym": root_node
        }
        super().__init__(message)


class CannotAttachOptionIfNotPresentIn2MOptionListException(BusinessException):
    def __init__(self, root_node: 'Node', options: List['Node']):
        message = ngettext(
            "Option \"%(code)s\" must be present in %(root_code)s program.",
            "Options \"%(code)s\" must be present in %(root_code)s program.",
            len(options)
        ) % {
            "code": ', '.join([str(option) for option in options]),
            "root_code": root_node
        }
        super().__init__(message)


class ReferenceLinkNotAllowedWithLearningUnitException(BusinessException):
    def __init__(self, learning_unit_node: 'Node', **kwargs):
        message = _("You are not allowed to create a reference with a learning unit %(child_node)s") % {
            "child_node": learning_unit_node
        }
        super().__init__(message, **kwargs)


class LinkShouldBeReferenceException(BusinessException):
    def __init__(self, parent_node: 'Node', child_node: 'Node', **kwargs):
        message = _("Link type should be reference between %(parent)s and %(child)s") % {
            "parent": parent_node,
            "child": child_node
        }
        super().__init__(message, **kwargs)


class ReferenceLinkNotAllowedException(BusinessException):
    def __init__(self, parent_node: 'Node', child_node: 'Node', reference_childrens: Iterable['Node'], **kwargs):
        message = _(
            "Link between %(parent)s and %(child)s cannot be of reference type "
            "because of its children: %(children)s"
        ) % {
            "parent": self._format_node(parent_node),
            "child": self._format_node(child_node),
            "children": ", ".join([self._format_node(reference_children) for reference_children in reference_childrens])
        }
        super().__init__(message, **kwargs)

    def _format_node(self, node: 'Node') -> str:
        return "{} ({})".format(str(node), node.node_type.value)


class InvalidBlockException(BusinessException):
    def __init__(self):
        message = _(
            "Please register a maximum of %(max_authorized_value)s digits in ascending order, "
            "without any duplication. Authorized values are from 1 to 6. Examples: 12, 23, 46"
        ) % {'max_authorized_value': BLOCK_MAX_AUTHORIZED_VALUE}
        super().__init__(message)


class BulkUpdateLinkException(Exception):
    def __init__(self, exceptions: Dict[str, 'MultipleBusinessExceptions']):
        self.exceptions = exceptions


class CannotPasteToLearningUnitException(BusinessException):
    def __init__(self, parent_node):
        message = _("Cannot add any element to learning unit %(parent_node)s") % {
            "parent_node": parent_node
        }
        super().__init__(message)


class CannotAttachSameChildToParentException(BusinessException):
    def __init__(self, child_node):
        message = _("You can not add the same child %(child_node)s several times.") % {"child_node": child_node}
        super().__init__(message)


class CannotAttachParentNodeException(BusinessException):
    def __init__(self, child_node: 'Node'):
        message = _('The child %(child)s you want to attach is a parent of the node you want to attach.') % {
            'child': child_node
        }
        super().__init__(message)


class ParentAndChildMustHaveSameAcademicYearException(BusinessException):
    def __init__(self, parent_node, child_node):
        message = _("It is prohibited to attach a %(child_node)s to an element of "
                    "another academic year %(parent_node)s.") % {
            "child_node": child_node,
            "parent_node": parent_node
        }
        super().__init__(message)


class CannotPasteNodeToHimselfException(BusinessException):
    def __init__(self, child_node: 'Node'):
        message = _('Cannot attach a node %(node)s to himself.') % {"node": child_node}
        super().__init__(message)


class ChildTypeNotAuthorizedException(BusinessException):
    def __init__(self, parent_node: 'Node', children_nodes: List['Node']):
        message = _(
            "You cannot add \"%(child)s\" to \"%(parent)s\" of type \"%(parent_type)s\""
        ) % {
            'child': ', '.join([self._format_node(children_node) for children_node in children_nodes]),
            'parent': parent_node,
            'parent_type': parent_node.node_type.value,
        }
        super().__init__(message)

    def _format_node(self, node: 'Node') -> str:
        return "{} ({})".format(str(node), node.node_type.value)


class MaximumChildTypesReachedException(BusinessException):
    def __init__(self, parent_node: 'Node', child_node: 'Node', node_types):
        message = _(
            "Cannot add \"%(child)s\" because the number of children of type(s) \"%(child_types)s\" "
            "for \"%(parent)s\" has already reached the limit.") % {
            'child': child_node,
            'child_types': ','.join([str(node_type.value) for node_type in node_types]),
            'parent': parent_node
        }
        super().__init__(message)


class MinimumEditableYearException(BusinessException):
    def __init__(self):
        message = _("Cannot perform action on a education group before %(limit_year)s") % {
            "limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION
        }
        super().__init__(message)
