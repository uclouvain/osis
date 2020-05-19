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
from typing import Optional

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from base.models.education_group_year import EducationGroupYear
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import ElementCache
from base.views.education_groups.select import get_clipboard_content_display, build_success_json_response
from program_management.models.enums.node_type import NodeType


@require_http_methods(['POST'])
def copy_to_cache(request):
    element_id = request.POST['element_id']
    element_type = request.POST['element_type']

    element = _get_concerned_object(element_id, element_type)

    return _cache_object(
        request.user,
        None,
        object_to_cache=element,
        action=ElementCache.ElementCacheAction.COPY
    )


@require_http_methods(['POST'])
def cut_to_cache(request):
    link_id = request.POST['group_element_year_id']
    element_id = request.POST['element_id']
    element_type = request.POST['element_type']

    element = _get_concerned_object(element_id, element_type)

    return _cache_object(
        request.user,
        link_id,
        object_to_cache=element,
        action=ElementCache.ElementCacheAction.CUT
    )


def _get_concerned_object(element_id: int, element_type: str):
    if element_type == NodeType.LEARNING_UNIT.name:
        object_class = LearningUnitYear
    else:
        object_class = EducationGroupYear

    return get_object_or_404(object_class, pk=element_id)


def _cache_object(
        user: User,
        link_id: Optional[int],
        object_to_cache,
        action: ElementCache.ElementCacheAction
):
    ElementCache(user).save_element_selected(object_to_cache, source_link_id=link_id, action=action.value)
    success_msg = get_clipboard_content_display(object_to_cache, action.value)
    return build_success_json_response(success_msg)
