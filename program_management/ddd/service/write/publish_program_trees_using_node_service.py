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
from threading import Thread
from typing import List

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction

from program_management.ddd.business_types import *
from base.business.education_groups.general_information import PublishException
from program_management.ddd.command import PublishProgramTreesVersionUsingNodeCommand, GetProgramTreesFromNodeCommand
from program_management.ddd.service.read import search_program_trees_using_node_service


@transaction.atomic()
def publish_program_trees_using_node(cmd: PublishProgramTreesVersionUsingNodeCommand) -> List['ProgramTreeIdentity']:
    if not all([settings.ESB_API_URL, settings.ESB_AUTHORIZATION, settings.ESB_REFRESH_PEDAGOGY_ENDPOINT]):
        raise ImproperlyConfigured('ESB_API_URL / ESB_AUTHORIZATION / ESB_REFRESH_PEDAGOGY_ENDPOINT' 
                                   'must be set in configuration')

    cmd = GetProgramTreesFromNodeCommand(code=cmd.code, year=cmd.year)
    program_trees = search_program_trees_using_node_service.search_program_trees_using_node(cmd)
    nodes_to_publish = [program_tree.root_node for program_tree in program_trees]
    t = Thread(target=_bulk_publish, args=(nodes_to_publish,))
    t.start()
    return [program_tree.entity_id for program_tree in program_trees]


def _bulk_publish(nodes: List['NodeGroupYear']) -> None:
    error_msgs = []
    for node in nodes:
        publish_url = __get_publish_url(node)
        try:
            __publish(publish_url)
        except Exception:
            error_msg = "Unable to publish sections for the program {code} - {year}".format(
                code=node.code, year=node.year
            )
            error_msgs.append(error_msg)

    if error_msgs:
        raise PublishException(",".join(error_msgs))


def __publish(publish_url: str):
    return requests.get(
        publish_url,
        headers={"Authorization": settings.ESB_AUTHORIZATION},
        timeout=settings.REQUESTS_TIMEOUT
    )


def __get_publish_url(node: 'NodeGroupYear') -> str:
    code_computed_for_esb = node.title
    if node.is_minor():
        code_computed_for_esb = "min-{}".format(node.code)
    elif node.is_deepening():
        code_computed_for_esb = "app-{}".format(node.code)
    elif node.is_major():
        code_computed_for_esb = "fsa1ba-{}".format(node.code)

    endpoint = settings.ESB_REFRESH_PEDAGOGY_ENDPOINT.format(year=node.year, code=code_computed_for_esb)
    return "{esb_api}/{endpoint}".format(esb_api=settings.ESB_API_URL, endpoint=endpoint)
