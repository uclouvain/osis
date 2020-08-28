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
import logging
from threading import Thread
from typing import List

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse

from program_management.ddd import command as command_program_management
from program_management.ddd.business_types import *
from program_management.ddd.service.read import search_program_trees_using_node_service

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def publish_group_year(code: str, year: int) -> bool:
    if not all([settings.ESB_API_URL, settings.ESB_AUTHORIZATION, settings.ESB_REFRESH_PEDAGOGY_ENDPOINT,
                settings.ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT,
                settings.ESB_REFRESH_COMMON_ADMISSION_ENDPOINT]):
        raise ImproperlyConfigured('ESB_API_URL / ESB_AUTHORIZATION / ESB_REFRESH_PEDAGOGY_ENDPOINT / '
                                   'ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT /  '
                                   'ESB_REFRESH_COMMON_ADMISSION_ENDPOINT must be set in configuration')

    if code == 'common':
        endpoint = settings.ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT.format(year=year)
        url = "{esb_api}/{endpoint}".format(esb_api=settings.ESB_API_URL, endpoint=endpoint)
        _publish(url, code, year)
    elif code.startswith('common'):
        endpoint = settings.ESB_REFRESH_COMMON_ADMISSION_ENDPOINT.format(year=year)
        url = "{esb_api}/{endpoint}".format(esb_api=settings.ESB_API_URL, endpoint=endpoint)
        _publish(url, code, year)
    else:
        cmd = command_program_management.GetProgramTreesFromNodeCommand(code=code, year=year)
        program_trees = search_program_trees_using_node_service.search_program_trees_using_node(cmd)
        nodes_to_publish = [program_tree.root_node for program_tree in program_trees]
        t = Thread(target=_bulk_publish, args=(nodes_to_publish,))
        t.start()
    return True


def _bulk_publish(nodes: List['NodeGroupYear']) -> None:
    for node in nodes:
        code_computed_for_esb = _get_code_computed_according_type(node)
        endpoint = settings.ESB_REFRESH_PEDAGOGY_ENDPOINT.format(year=node.year, code=code_computed_for_esb)
        url = "{esb_api}/{endpoint}".format(esb_api=settings.ESB_API_URL, endpoint=endpoint)
        _publish(url, node.code, node.year)


def _publish(publish_url: str, code: str, year: int) -> bool:
    try:
        response = requests.get(
            publish_url,
            headers={"Authorization": settings.ESB_AUTHORIZATION},
            timeout=settings.REQUESTS_TIMEOUT
        )
        if response.status_code != HttpResponse.status_code:
            logger.info(
                "The program {code} - {year} has no page to publish on it".format(code=code, year=year)
            )
            return False
        return True
    except Exception:
        error_msg = "Unable to publish sections for the program {code} - {year}".format(
            code=code,
            year=year
        )
        raise PublishException(error_msg)


def _get_code_computed_according_type(node: 'NodeGroupYear') -> str:
    code_computed_for_esb = node.title
    if node.is_minor():
        code_computed_for_esb = "min-{}".format(node.code)
    elif node.is_deepening():
        code_computed_for_esb = "app-{}".format(node.code)
    elif node.is_major():
        code_computed_for_esb = "fsa1ba-{}".format(node.code)
    return code_computed_for_esb


class PublishException(Exception):
    """Some kind of problem with a publish to ESB. """
    pass
