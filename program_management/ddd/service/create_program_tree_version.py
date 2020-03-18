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
from typing import List

from base.models.enums.link_type import LinkTypes
from program_management.ddd.business_types import *
from base.ddd.utils.validation_message import BusinessValidationMessage
from program_management.ddd.domain.node import factory
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.models.enums.node_type import NodeType
from program_management.ddd.repositories import load_tree, persist_tree
from program_management.ddd.validators._attach_finality_end_date import AttachFinalityEndDateValidator
from program_management.ddd.validators._attach_option import AttachOptionsValidator
from program_management.ddd.validators._authorized_relationship import AttachAuthorizedRelationshipValidator


RootID = int

def create_new_program(
        create_from: RootID = None,
        until_year: int = None,
        **program_attrs
) -> List[BusinessValidationMessage]:
    new_tree = ProgramTreeVersion(
        factory.get_node(NodeType.EDUCATION_GROUP.name),
        program_attrs['version_type'],
        program_attrs['version_name'],
    )
    persist_tree.persist(new_tree)
    return success_messages

# Comment gérer les créations?
# Comment gérer les ModelChoiceFields + filtres sur les forms? (Appel à repository qui renvoie un queryset?) (exemple : date de fin, liste de choi
# Comment gérer les permissions? (Exemple : bouton 'créer pgm transition' grisé si programme de transition existe déjà).
