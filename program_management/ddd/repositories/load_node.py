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

from django.db.models import F, Value, CharField, QuerySet, Case, When, IntegerField, OuterRef, Subquery, Q
from django.db.models.functions import Concat

from base.models.entity_version import EntityVersion
from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.education_group_types import EducationGroupTypesEnum, GroupType, TrainingType, MiniTrainingType
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.schedule_type import ScheduleTypeEnum
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_year import LearningUnitYear
from education_group.models.enums.constraint_type import ConstraintTypes
from education_group.models.group_year import GroupYear
from program_management.ddd.domain import node
from program_management.ddd.domain._campus import Campus
from program_management.models import element
from program_management.models.enums.node_type import NodeType


def load(element_id: int) -> node.Node:
    try:
        return load_multiple([element_id])[0]
    except IndexError:
        raise node.NodeNotFoundException


# TODO :: create a new app group/ddd and move the fetch of Group, GroupYear into this new app? (like learning_unit?)
def load_multiple(element_ids: List[int]) -> List[node.Node]:
    qs = element.Element.objects.filter(
        pk__in=element_ids
    ).annotate(
        node_type=Case(
            When(group_year_id__isnull=False, then=Value(NodeType.GROUP.name)),
            When(learning_unit_year_id__isnull=False, then=Value(NodeType.LEARNING_UNIT.name)),
            When(learning_class_year_id__isnull=False, then=Value(NodeType.LEARNING_CLASS.name)),
            default=Value("Unknown"),
            output_field=CharField(),
        ),
        fk_id=Case(
            When(group_year_id__isnull=False, then=F('group_year_id')),
            When(learning_unit_year_id__isnull=False, then=F('learning_unit_year_id')),
            When(learning_class_year_id__isnull=False, then=F('learning_class_year_id')),
            default=Value(-1),
            output_field=IntegerField(),
        )
    ).values('node_type', 'fk_id', 'pk')

    # Create data-structure which all to get in a fast way the corresponding element id of the foreign key id
    elements_group_by_type = {}
    for elem in qs:
        elements_group_by_type.setdefault(elem['node_type'], {})
        elements_group_by_type[elem['node_type']][elem['fk_id']] = elem['pk']

    nodes_objects = []
    for node_type, elem_grouped in elements_group_by_type.items():
        get_method = {
            NodeType.GROUP.name: __load_multiple_node_group_year,
            NodeType.LEARNING_UNIT.name: __load_multiple_node_learning_unit_year
        }[node_type]

        nodes_objects += [
            __instanciate_node(**node_data, node_id=elem_grouped[node_data.pop('id')])
            for node_data in get_method(elem_grouped.keys())
        ]
    return nodes_objects


def __instanciate_node(**node_attrs):
    if node_attrs.get('teaching_campus_name'):
        node_attrs['teaching_campus'] = Campus(
            name=node_attrs.pop('teaching_campus_name'),
            university_name=node_attrs.pop('teaching_campus_university_name'),
        )
    return node.factory.get_node(**__convert_string_to_enum(node_attrs))


def __convert_string_to_enum(node_data: dict) -> dict:
    if node_data.get('node_type'):
        node_data['node_type'] = convert_node_type_enum(node_data['node_type'])
    if node_data.get('category'):
        node_data['category'] = __convert_category_enum(node_data['category'])
    if node_data.get('periodicity'):
        node_data['periodicity'] = PeriodicityEnum[node_data['periodicity']]
    if node_data.get('schedule_type'):
        node_data['schedule_type'] = ScheduleTypeEnum[node_data['schedule_type']]
    if node_data.get('constraint_type'):
        node_data['constraint_type'] = ConstraintTypes[node_data['constraint_type']]
    if node_data.get('offer_status'):
        node_data['offer_status'] = ActiveStatusEnum[node_data['offer_status']]
    node_data['type'] = NodeType[node_data['type']]
    return node_data


def convert_node_type_enum(str_node_type: str) -> EducationGroupTypesEnum:
    enum_node_type = None
    for sub_enum in EducationGroupTypesEnum.__subclasses__():
        try:
            enum_node_type = sub_enum[str_node_type]
        except KeyError:
            pass
    if not enum_node_type:
        raise KeyError("Cannot convert '{}' str type to '{}' type".format(str_node_type, EducationGroupTypesEnum))
    return enum_node_type


def __convert_category_enum(category: str):
    return getattr(GroupType, category, None) or getattr(TrainingType, category, None) or \
           getattr(MiniTrainingType, category, None)


def __load_multiple_node_group_year(node_group_year_ids: List[int]) -> QuerySet:
    subquery_management_entity = EntityVersion.objects.filter(
        entity=OuterRef('management_entity'),
    ).current(
        OuterRef('academic_year__start_date')
    ).values('acronym')[:1]

    return GroupYear.objects.filter(pk__in=node_group_year_ids).annotate(
        type=Value(NodeType.GROUP.name, output_field=CharField()),
        node_type=F('education_group_type__name'),
        category=F('education_group_type__name'),
        code=F('partial_acronym'),
        title=F('acronym'),
        year=F('academic_year__year'),
        start_year=F('group__start_year__year'),
        end_year=F('group__end_year__year'),
        management_entity_acronym=Subquery(subquery_management_entity),
        teaching_campus_name=F('main_teaching_campus__name'),
        teaching_campus_university_name=F('main_teaching_campus__organization__name'),
        offer_partial_title_fr=F('educationgroupversion__offer__partial_title'),
        offer_partial_title_en=F('educationgroupversion__offer__partial_title_english'),
        offer_title_fr=F('educationgroupversion__offer__title'),
        offer_title_en=F('educationgroupversion__offer__title_english'),
        offer_status=F('educationgroupversion__offer__active'),
        version_name=F('educationgroupversion__version_name'),
        version_title_fr=F('educationgroupversion__title_fr'),
        version_title_en=F('educationgroupversion__title_en'),
        schedule_type=F('educationgroupversion__offer__schedule_type'),
        keywords=F('educationgroupversion__offer__keywords'),
        group_title_fr=F('title_fr'),
        group_title_en=F('title_en'),
    ).values(
        'id',
        'type',
        'node_type',
        'code',
        'title',
        'year',
        'start_year',
        'end_year',
        'constraint_type',
        'min_constraint',
        'max_constraint',
        'remark_fr',
        'remark_en',
        'credits',

        'offer_partial_title_fr',
        'offer_partial_title_en',
        'offer_title_fr',
        'offer_title_en',
        'group_title_fr',
        'group_title_en',
        'version_name',
        'version_title_fr',
        'version_title_en',
        'schedule_type',
        'offer_status',
        'keywords',
        'category',
        'management_entity_acronym',
        'teaching_campus_name',
        'teaching_campus_university_name',
    )


def __load_multiple_node_learning_unit_year(node_learning_unit_year_ids: List[int]):
    subquery_component = LearningComponentYear.objects.filter(
        learning_unit_year_id=OuterRef('pk')
    )
    subquery_component_pm = subquery_component.filter(
        type=LECTURING
    )
    subquery_component_pp = subquery_component.filter(
        type=PRACTICAL_EXERCISES
    )
    return LearningUnitYear.objects.filter(
        id__in=node_learning_unit_year_ids
    ).annotate(
        type=Value(NodeType.LEARNING_UNIT.name, output_field=CharField()),
        learning_unit_type=F('learning_container_year__container_type'),
        year=F('academic_year__year'),
        proposal_type=F('proposallearningunit__type'),
        code=F('acronym'),
        title=Case(
            When(Q(specific_title__isnull=False) & ~Q(specific_title__exact='') &
                 Q(learning_container_year__common_title__isnull=False) &
                 ~Q(learning_container_year__common_title__exact=''), then=Concat(
                'learning_container_year__common_title', Value(' - '), 'specific_title',
                output_field=CharField()
            )),
            When(Q(specific_title__isnull=False) & ~Q(specific_title__exact=''), then=F("specific_title")),
            When(Q(learning_container_year__common_title__isnull=False) &
                 ~Q(learning_container_year__common_title__exact=''), then=F('learning_container_year__common_title')
                 ),
            default=Value("")
        ),
        specific_title_en=F('specific_title_english'),
        specific_title_fr=F('specific_title'),
        common_title_fr=F('learning_container_year__common_title'),
        common_title_en=F('learning_container_year__common_title_english'),
        other_remark=F('learning_unit__other_remark'),
        volume_total_lecturing=Subquery(subquery_component_pm.values('hourly_volume_total_annual')),
        volume_total_practical=Subquery(subquery_component_pp.values('hourly_volume_total_annual')),

    ).values(
        'id',
        'type',
        'learning_unit_type',
        'year',
        'proposal_type',
        'code',
        'title',
        'credits',
        'status',
        'periodicity',
        'common_title_fr',
        'specific_title_fr',
        'common_title_en',
        'specific_title_en',
        'other_remark',
        'quadrimester',
        'volume_total_lecturing',
        'volume_total_practical',
    )
