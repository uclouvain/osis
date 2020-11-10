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
from program_management.ddd.business_types import *
from program_management.ddd.domain.exception import ProgramTreeVersionNotFoundException
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository


def format_program_tree_version_identity(tree_version_identity: 'ProgramTreeVersionIdentity') -> str:
    if tree_version_identity.version_name:
        return "{}[{}]".format(tree_version_identity.offer_acronym, tree_version_identity.version_name)
    return tree_version_identity.offer_acronym


def format_program_tree_version_complete_title(tree_version_identity: 'ProgramTreeVersionIdentity') -> str:
    return "%(offer_acronym)s %(version_name)s%(title)s" % {
            'offer_acronym': tree_version_identity.offer_acronym,
            'version_name': "[{}{}]".format(
                tree_version_identity.version_name,
                '-Transition' if tree_version_identity.is_transition else ''
            ) if tree_version_identity.version_name else '',
            'title': _build_title(tree_version_identity),
        }


def _build_title(tree_version_identity):
    try:
        program_tree_version = ProgramTreeVersionRepository.get(tree_version_identity)
        offer_title = " - {}".format(
            program_tree_version.get_tree().root_node.offer_title_fr
        ) if program_tree_version.get_tree().root_node.offer_title_fr else ''
        version_title = "[{}]".format(program_tree_version.title_fr) if program_tree_version.title_fr else ''
        return "{}{}".format(offer_title, version_title)

    except ProgramTreeVersionNotFoundException:
        return ''
