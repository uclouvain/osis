#############################################################################
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
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from education_group.ddd.domain.exception import GroupNotFoundException

from program_management.ddd import command
from program_management.ddd.service.write import copy_element_service, cut_element_service
from education_group.ddd import command as command_education_group
from education_group.ddd.service.read import get_group_service
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.service.identity_search import ProgramTreeVersionIdentitySearch

MESSAGE_TEMPLATE = "<strong>{clipboard_title}</strong><br>{object_str}"


@require_http_methods(['POST'])
@login_required
def copy_to_cache(request):
    element_code = request.POST['element_code']
    element_year = int(request.POST['element_year'])
    copy_command = command.CopyElementCommand(request.user.id, element_code, element_year)

    copy_element_service.copy_element_service(copy_command)
    cmd = command_education_group.GetGroupCommand(code=element_code, year=element_year)

    try:
        group_obj = get_group_service.get_group(cmd)
        node_identity = NodeIdentity(code=element_code, year=element_year)
        version_identity = ProgramTreeVersionIdentitySearch().get_from_node_identity(node_identity)
        success_msg = MESSAGE_TEMPLATE.format(
            clipboard_title=_("Copied element"),
            object_str="{} - {}{} - {}".format(
                element_code,
                group_obj.abbreviated_title,
                "[{}]".format(version_identity.version_name) if version_identity.version_name else '',
                element_year
            ),
        )
    except GroupNotFoundException:
        success_msg = MESSAGE_TEMPLATE.format(
            clipboard_title=_("Copied element"),
            object_str="{} - {}".format(element_code, element_year),
        )

    return JsonResponse({'success_message': success_msg})


@require_http_methods(['POST'])
def cut_to_cache(request):
    path_to_detach = request.POST['path_to_detach']
    element_code = request.POST['element_code']
    element_year = int(request.POST['element_year'])
    cut_command = command.CutElementCommand(request.user.id, element_code, element_year, path_to_detach)

    cut_element_service.cut_element_service(cut_command)

    success_msg = MESSAGE_TEMPLATE.format(
        clipboard_title=_("Cut element"),
        object_str="{} - {}".format(element_code, element_year),
    )

    return JsonResponse({'success_message': success_msg})
