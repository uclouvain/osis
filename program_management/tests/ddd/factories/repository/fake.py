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
from typing import List, Type

from osis_common.ddd import interface
from program_management.ddd import command
from program_management.ddd.business_types import *
from program_management.ddd.domain import exception
from testing.mocks import FakeRepository


def get_fake_program_tree_repository(root_entities: List['ProgramTree']) -> Type['FakeRepository']:
    class_name = "FakeProgramTreeRepository"
    return type(class_name, (FakeRepository,), {
        "root_entities": root_entities.copy(),
        "not_found_exception_class": exception.ProgramTreeNotFoundException,
        "delete": _delete_program_tree
    })


def get_fake_program_tree_version_repository(root_entities: List['ProgramTreeVersion']) -> Type['FakeRepository']:
    class_name = "FakeProgramTreeVersionRepository"
    return type(class_name, (FakeRepository,), {
        "root_entities": root_entities.copy(),
        "not_found_exception_class": exception.ProgramTreeVersionNotFoundException,
        "delete": _delete_program_tree_version
    })


@classmethod
def _delete_program_tree_version(
        cls,
        entity_id: 'ProgramTreeVersionIdentity',
        delete_program_tree_service: interface.ApplicationService) -> None:
    tree_version = cls.get(entity_id)

    idx = -1
    for idx, entity in enumerate(cls.root_entities):
        if entity.entity_id == entity_id:
            break
    if idx >= 0:
        cls.root_entities.pop(idx)

    cmd = command.DeleteProgramTreeCommand(code=tree_version.tree.root_node.code, year=tree_version.tree.root_node.year)
    delete_program_tree_service(cmd)


@classmethod
def _delete_program_tree(
        cls,
        entity_id: 'ProgramTreeIdentity',
        delete_node_service: interface.ApplicationService) -> None:
    program_tree = cls.get(entity_id)
    nodes = program_tree.get_all_nodes()

    idx = -1
    for idx, entity in enumerate(cls.root_entities):
        if entity.entity_id == entity_id:
            break
    if idx >= 0:
        cls.root_entities.pop(idx)

    for node in nodes:
        cmd = command.DeleteNodeCommand(code=node.code, year=node.year, node_type=node.node_type.name,
                                        acronym=node.title)
        delete_node_service(cmd)
