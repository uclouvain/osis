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
from django.db import transaction

from base.models import entity_version
from base.models.academic_year import AcademicYear
from base.models.campus import Campus
from base.models.education_group_type import EducationGroupType
from base.models.group_element_year import GroupElementYear
from education_group.models.group import Group
from education_group.models.group_year import GroupYear
from osis_common.decorators.deprecated import deprecated
from program_management.ddd.domain import program_tree
from program_management.ddd.domain.node import Node, NodeGroupYear
from program_management.ddd.repositories import _persist_prerequisite
from program_management.models.element import Element


@deprecated  # use ProgramTreeRepository.create() or .update() instead
@transaction.atomic
def persist(tree: program_tree.ProgramTree) -> None:
    __update_or_create_nodes(tree)
    __update_or_create_links(tree.root_node)
    __delete_links(tree, tree.root_node)
    _persist_prerequisite.persist(tree)


# TODO :: to move into "Group" repository (another domain)
def __update_or_create_nodes(tree: program_tree.ProgramTree):
    for node in tree.get_all_nodes():
        if node._has_changed and node.is_group_or_mini_or_training():
            group = __update_or_create_group_model(node)
            group_year = __update_or_create_group_year_model(node, group)
            element = __update_or_create_element_model(group_year)


def __update_or_create_group_model(node: 'NodeGroupYear') -> Group:
    group, created = Group.objects.update_or_create(
        pk=node.not_annualized_id.uuid,
        defaults={
            'start_year': AcademicYear.objects.get(year=node.start_year),
            'end_year': AcademicYear.objects.get(year=node.end_date) if node.end_date else None,
        }
    )
    group.save()
    return group


def __update_or_create_group_year_model(node: 'NodeGroupYear', group: Group) -> GroupYear:
    entity = entity_version.find(
        node.management_entity_acronym
    ).entity_id if node.management_entity_acronym else None
    group_year, created = GroupYear.objects.update_or_create(
        partial_acronym=node.code,
        academic_year=AcademicYear.objects.get(year=node.year),
        defaults={
            'acronym': node.title,
            'education_group_type': EducationGroupType.objects.get(name=node.node_type.name) if node.node_type else None,
            'credits': node.credits,
            'constraint_type': node.constraint_type,
            'min_constraint': node.min_constraint,
            'max_constraint': node.max_constraint,
            'group': group,
            'title_fr': node.group_title_fr,
            'title_en': node.group_title_en,
            'remark_fr': node.remark_fr,
            'remark_en': node.remark_en,
            'management_entity': entity,
            'main_teaching_campus': Campus.objects.get(name=node.teaching_campus).pk if node.teaching_campus else None,
            # 'active': node.status,  # FIXME :: to implement in Repository.get() !
        }
    )
    return group_year


def __update_or_create_element_model(group_year: GroupYear) -> Element:
    element, created = Element.objects.get_or_create(group_year=group_year)
    return element


def __update_or_create_links(node: Node):
    for link in node.children:
        if link.has_changed:
            __persist_group_element_year(link)

        __update_or_create_links(link.child)


def __persist_group_element_year(link):
    group_element_year, _ = GroupElementYear.objects.update_or_create(
        parent_element_id=link.parent.pk,
        child_element_id=link.child.pk,
        defaults={
            'relative_credits': link.relative_credits,
            'min_credits': link.min_credits,
            'max_credits': link.max_credits,
            'is_mandatory': link.is_mandatory,
            'block': link.block,
            'access_condition': link.access_condition,
            'comment': link.comment,
            'comment_english': link.comment_english,
            'own_comment': link.own_comment,
            'quadrimester_derogation': link.quadrimester_derogation,
            'link_type': link.link_type,
            'order': link.order,

        }
    )


def __delete_links(tree: program_tree.ProgramTree, node: Node):
    for link in node._deleted_children:
        if link.child.is_learning_unit():
            _persist_prerequisite._persist(tree.root_node, link.child)
        __delete_group_element_year(link)
    for link in node.children:
        __delete_links(tree, link.child)


def __delete_group_element_year(link):
    GroupElementYear.objects.filter(pk=link.pk).delete()
