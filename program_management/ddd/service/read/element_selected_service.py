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
from typing import List, Tuple, Optional

from django.contrib.auth import models

from base.utils import cache
from program_management.models.enums.node_type import NodeType


def retrieve_element_selected(user: models.User, ids: List[int], content_type: Optional[str]) -> List:
    def _convert_element_to_node_id_and_node_type(element) -> Tuple[int, NodeType, int]:
        if element['modelname'] == NodeType.LEARNING_UNIT.name:
            return element["id"], NodeType.LEARNING_UNIT, element.get("source_link_id")
        return element["id"], NodeType.EDUCATION_GROUP, element.get("source_link_id")

    if ids:
        selected_elements = [{"id": object_id, "modelname": content_type} for object_id in ids]
    else:
        selected_element_in_cache = cache.ElementCache(user).cached_data
        selected_elements = [selected_element_in_cache] if selected_element_in_cache else []
    return [_convert_element_to_node_id_and_node_type(element) for element in selected_elements]
