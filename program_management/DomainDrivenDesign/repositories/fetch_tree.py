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
from typing import List

from django.db.models import Case, F, When, IntegerField

from base.models.group_element_year import GroupElementYear

from program_management.DomainDrivenDesign.domain import node, link
from program_management.DomainDrivenDesign.domain.program_tree import ProgramTree
from program_management.DomainDrivenDesign.repositories import fetch_node, fetch_prerequisite, \
    fetch_authorized_relationship


def fetch(tree_root_id) -> ProgramTree:
    root_node = fetch_node.fetch_node_education_group_year(tree_root_id)

    structure = GroupElementYear.objects.get_adjacency_list([root_node.pk])
    nodes = __fetch_tree_nodes(structure)
    links = __fetch_tree_links(structure)
    prerequisites = __fetch_tree_prerequisites(tree_root_id, nodes)
    return __build_tree(root_node, structure, nodes, links, prerequisites)


def fetch_trees_from_children(child_branch_ids: list, child_leaf_ids: list = None) -> List[ProgramTree]:
    # FIXME :: simplify the code (child_branch, chlid_leaf, if else)
    if not child_branch_ids and not child_leaf_ids:
        return []
    if child_branch_ids:
        assert isinstance(child_branch_ids, list)
    if child_leaf_ids:
        assert isinstance(child_leaf_ids, list)
    qs = GroupElementYear.objects.get_reverse_adjacency_list(
        child_branch_ids=child_branch_ids,
        child_leaf_ids=child_leaf_ids
    )
    if not qs:
        root_ids = child_branch_ids
    else:
        all_parents = set(obj['parent_id'] for obj in qs)
        parent_by_child_branch = {
            obj['child_id']: obj['parent_id'] for obj in qs
        }
        root_ids = set(
            parent_id for parent_id in all_parents
            if not parent_by_child_branch.get(parent_id)
        )
    # TODO :: performance (get all trees in one single query)
    return [fetch(root_id) for root_id in root_ids]


def __fetch_tree_nodes(tree_structure):
    ids = [link['id'] for link in tree_structure]
    nodes_list = fetch_node.fetch_multiple(ids)
    return {n.pk: n for n in nodes_list}


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


def __fetch_tree_prerequisites(tree_root_id: int, nodes: dict):
    node_leaf_ids = [n.pk for n in nodes.values() if isinstance(n, node.NodeLearningUnitYear)]
    has_prerequisite_dict = fetch_prerequisite.fetch_has_prerequisite(tree_root_id, node_leaf_ids)
    is_prerequisite_dict = {
        main_node_id: [nodes[id] for id in node_ids]
        for main_node_id, node_ids in fetch_prerequisite.fetch_is_prerequisite(tree_root_id, node_leaf_ids).items()
    }
    return {'has_prerequisite_dict': has_prerequisite_dict, 'is_prerequisite_dict': is_prerequisite_dict}


def __build_tree(root_node, tree_structure, nodes, links, prerequisites):
    root_node.children = __build_children(root_node, tree_structure, nodes, links, prerequisites)
    tree = ProgramTree(root_node, authorized_relationships=fetch_authorized_relationship.fetch())
    return tree


def __build_children(root, tree_structure, nodes, links, prerequisites):
    children = []

    for child_structure in [structure for structure in tree_structure if structure['parent_id'] == root.pk]:
        child_node = copy.deepcopy(nodes[child_structure['child_id']])
        child_node.children = __build_children(child_node, tree_structure, nodes, links, prerequisites)

        if isinstance(child_node, node.NodeLearningUnitYear):
            child_node.prerequisite = prerequisites['has_prerequisite_dict'].get(child_node.pk, [])
            child_node.is_prerequisite_of = prerequisites['is_prerequisite_dict'].get(child_node.pk, [])

        link_node = copy.deepcopy(
            links['_'.join([str(child_structure['parent_id']), str(child_structure['child_id'])])]
        )
        link_node.parent = root
        link_node.child = child_node
        children.append(link_node)
    return children
