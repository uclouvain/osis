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

import copy

from django.db.models import Case, Value, F, When, IntegerField, CharField

from base.models.group_element_year import GroupElementYear
from program_management.domain import node, link
from program_management.domain.program_tree import ProgramTree
from program_management.models.element import Element
from program_management.models.enums import node_type


def fetch(tree_root_id) -> ProgramTree:
    root_node = node.factory.get_node(
        **Element.objects.filter(education_group_year_id=tree_root_id).annotate(
            type=Value(node_type.EDUCATION_GROUP, output_field=CharField()),
            acronym=F('education_group_year__acronym'),
            title=F('education_group_year__title'),
            year=F('education_group_year__academic_year__year'),
            node_id=F('education_group_year__pk')
        ).values('node_id', 'type', 'acronym', 'title', 'year').get()
    )
    structure = GroupElementYear.objects.get_adjacency_list([root_node.pk])
    nodes = __fetch_tree_nodes(structure)
    links = __fetch_tree_links(structure)
    return __build_tree(root_node, structure, nodes, links)


def __fetch_tree_nodes(tree_structure):
    ids = [link['id'] for link in tree_structure]
    group_element_year_qs = GroupElementYear.objects.filter(pk__in=ids).annotate(
        node_id=Case(
            When(child_branch_id__isnull=True, then=F('child_leaf_id')),
            default=F('child_branch_id'),
            output_field=IntegerField()
        ),
        type=Case(
            When(child_branch_id__isnull=True, then=Value(node_type.LEARNING_UNIT)),
            default=Value(node_type.EDUCATION_GROUP),
            output_field=CharField()
        ),
        acronym=Case(
            When(child_branch_id__isnull=True, then=F('child_leaf__acronym')),
            default=F('child_branch__acronym'),
            output_field=CharField()
        ),
        title=Case(
            When(child_branch_id__isnull=True, then=F('child_leaf__specific_title')),
            default=F('child_branch__title'),
            output_field=CharField()
        ),
        year=Case(
            When(child_branch_id__isnull=True, then=F('child_leaf__academic_year__year')),
            default=F('child_branch__academic_year__year'),
            output_field=IntegerField()
        )
    ).values('node_id', 'type', 'acronym', 'title', 'year')
    nodes = {}
    for gey_dict in group_element_year_qs:
        nodes[gey_dict['node_id']] = node.factory.get_node(**gey_dict)
    return nodes


def __fetch_tree_links(tree_structure):
    group_element_year_ids = [link['id'] for link in tree_structure]
    group_element_year_qs = GroupElementYear.objects.filter(pk__in=group_element_year_ids).annotate(
        child_id=Case(
            When(child_branch_id__isnull=True, then=F('child_leaf_id')),
            default=F('child_branch_id'),
            output_field=IntegerField()
        )
    ).values(
        'relative_credits',
        'min_credits',
        'max_credits',
        'is_mandatory',
        'block',
        'comment',
        'comment_english',
        'own_comment',
        'quadrimester_derogation',
        'link_type',
        'parent_id',
        'child_id'
    )

    tree_links = {}
    for gey_dict in group_element_year_qs:
        parent_id = gey_dict.pop('parent_id')
        child_id = gey_dict.pop('child_id')

        tree_id = '_'.join([str(parent_id), str(child_id)])
        tree_links[tree_id] = link.factory.get_link(parent=None, child=None, **gey_dict)
    return tree_links


def __build_tree(root_node, tree_structure, nodes, links):
    root_node.children = __build_children(root_node, tree_structure, nodes, links)
    tree = ProgramTree(root_node)
    return tree


def __build_children(root, tree_structure, nodes, links):
    children = []

    for child_structure in [structure for structure in tree_structure if structure['parent_id'] == root.pk]:
        child_node = copy.deepcopy(nodes[child_structure['child_id']])
        child_node.children = __build_children(child_node, tree_structure, nodes, links)

        link_node = copy.deepcopy(
            links['_'.join([str(child_structure['parent_id']), str(child_structure['child_id'])])]
        )
        link_node.parent = root
        link_node.child = child_node
        children.append(link_node)
    return children
