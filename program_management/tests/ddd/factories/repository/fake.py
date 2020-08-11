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

from program_management.ddd.business_types import *
from program_management.ddd.domain import exception
from testing.mocks import FakeRepository


def get_fake_program_tree_repository(root_entities: List['ProgramTree']) -> Type['FakeRepository']:
    class_name = "FakeProgramTreeRepository"
    return type(class_name, (FakeRepository,), {
        "root_entities": root_entities,
        "not_found_exception_class": exception.ProgramTreeNotFoundException
    })


def get_fake_program_tree_version_repository(root_entities: List['ProgramTreeVersion']) -> Type['FakeRepository']:
    class_name = "FakeProgramTreeVersionRepository"
    return type(class_name, (FakeRepository,), {
        "root_entities": root_entities,
        "not_found_exception_class": exception.ProgramTreeVersionNotFoundException
    })
