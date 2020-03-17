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

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Value, Case, When, IntegerField, CharField, QuerySet, Q

from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear
from learning_unit.ddd.repository import load_learning_unit_year
from program_management.ddd.domain import node
from program_management.models.enums.node_type import NodeType

from learning_unit.ddd.business_types import *


def load_by_type(type: NodeType, element_id: int) -> node.Node:
    if type == NodeType.EDUCATION_GROUP:
        return load_node_education_group_year(element_id)
    elif type == NodeType.LEARNING_UNIT:
        return load_node_learning_unit_year(element_id)


def load_node_education_group_year(node_id: int) -> node.Node:
    try:
        node_data = __load_multiple_node_education_group_year([node_id])[0]
        return node.factory.get_node(**__convert_string_to_enum(node_data))
    except IndexError:
        raise node.NodeNotFoundException


def load_node_learning_unit_year(node_id: int) -> node.Node:
    try:
        node_data = __load_multiple_node_learning_unit_year([node_id])[0]
        return node.factory.get_node(**__convert_string_to_enum(node_data))
    except IndexError:
        raise node.NodeNotFoundException


def load_multiple(element_ids: List[int]) -> List[node.Node]:
    qs = GroupElementYear.objects.filter(
        pk__in=element_ids
    ).filter(
        Q(child_leaf__isnull=False) | Q(child_branch__isnull=False)
    ).annotate(
        node_id=F('child_branch__pk'),
        type=Value(NodeType.EDUCATION_GROUP.name, output_field=CharField()),
        code=F('child_branch__partial_acronym'),
        title=F('child_branch__acronym'),
        year=F('child_branch__academic_year__year'),
        learning_unit_year_id=F('child_leaf__pk'),
    ).values(
        'node_id', 'type', 'code', 'title', 'year', 'learning_unit_year_id',
    )

    nodes_data = list(qs)

    learning_unit_pks = list(node_data.pop('learning_unit_year_id') for node_data in nodes_data)

    nodes_objects = [node.factory.get_node(**__convert_string_to_enum(node_data)) for node_data in nodes_data]

    learn_units = load_learning_unit_year.load_multiple(learning_unit_pks)

    nodes_objects += __convert_to_node(learn_units)

    return nodes_objects


def __convert_to_node(learning_units: List['LearningUnitYear']) -> List[node.Node]:
    nodes = []
    for lu in learning_units:
        node_data = {
            'node_id': lu.id,
            'type': NodeType.LEARNING_UNIT.name,
            'year': lu.year,
            'proposal_type': lu.proposal_type,
            'code': lu.acronym,
            'title': lu.full_title_fr,
            'credits': lu.credits,
            'status': lu.credits,
            'periodicity': lu.credits,
        }
        nodes.append(node.factory.get_node(**__convert_string_to_enum(node_data)))
    return nodes


def __convert_string_to_enum(node_data: dict) -> dict:
    # TODO Enum.choices should return tuple((enum, enum.value) for enum in cls) ?
    node_data['type'] = NodeType[node_data['type']]
    return node_data


def __load_multiple_node_education_group_year(node_group_year_ids: List[int]) -> QuerySet:
    return EducationGroupYear.objects.filter(pk__in=node_group_year_ids).annotate(
        node_id=F('pk'),
        type=Value(NodeType.EDUCATION_GROUP.name, output_field=CharField()),
        node_code=F('partial_acronym'),
        node_title=F('acronym'),
        year=F('academic_year__year'),
        proposal_type=Value(None, output_field=CharField()),
    ).values('node_id', 'type', 'year', 'proposal_type', 'node_code', 'node_title', 'credits')\
     .annotate(title=F('node_title'), code=F('node_code'))\
     .values('node_id', 'type', 'year', 'proposal_type', 'code', 'title', 'credits')


def __load_multiple_node_learning_unit_year(node_learning_unit_year_ids: List[int]):
    return LearningUnitYear.objects.filter(pk__in=node_learning_unit_year_ids).annotate_full_title().annotate(
        node_id=F('pk'),
        type=Value(NodeType.LEARNING_UNIT.name, output_field=CharField()),
        node_code=F('acronym'),
        node_title=F('full_title'),
        year=F('academic_year__year'),
        proposal_type=F('proposallearningunit__type'),
    ).values('node_id', 'type', 'year', 'proposal_type', 'node_code', 'node_title', 'credits')\
     .annotate(title=F('node_title'), code=F('node_code'))\
     .values('node_id', 'type', 'year', 'proposal_type', 'code', 'title', 'credits')
