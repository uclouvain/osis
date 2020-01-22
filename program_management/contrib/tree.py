import copy

from base.models.group_element_year import GroupElementYear
from program_management.contrib.models import node, link
from program_management.contrib.models.education_group_program import EducationGroupProgram
from program_management.models.element import Element


def fetch(tree_root_id) -> EducationGroupProgram:
    root_node = node.factory.get_node(
        Element.objects.get(education_group_year_id=tree_root_id)
        # TODO: Change when migration is done : Element.objects.get(group_year_id=tree_root_id)
    )

    structure = GroupElementYear.objects.get_adjacency_list([root_node.pk])
    nodes = __fetch_tree_nodes(structure)
    links = __fetch_tree_links(structure)
    return __build_tree(root_node, structure, nodes, links)


# TODO: Change when migration is done : Use this __fetch_tree_nodes
# def __fetch_tree_nodes(tree_structure):
#     element_ids = [link['child_id'] for link in tree_structure]
#     element_qs = Element.objects.filter(pk__in=element_ids).select_related(
#         'education_group_year',
#         'group_year',
#         'learning_unit_year',
#         'learning_class_year'
#     )
#     return {element.pk: node.factory.get_node(element) for element in element_qs}

def __fetch_tree_nodes(tree_structure):
    """ This version is temporary see function above as definitive one"""
    ids = [link['id'] for link in tree_structure]
    group_element_year_qs = GroupElementYear.objects.filter(pk__in=ids).select_related(
        'child_branch',
        'child_leaf',
    )
    nodes = {}
    for gey in group_element_year_qs:
        if gey.child_branch_id:
            element = Element(education_group_year=gey.child_branch)
            nodes[gey.child_branch_id] = node.factory.get_node(element)
        elif gey.child_leaf:
            element = Element(learning_unit_year=gey.child_leaf)
            nodes[gey.child_leaf_id] = node.factory.get_node(element)
    return nodes


def __fetch_tree_links(tree_structure):
    group_element_year_ids = [link['id'] for link in tree_structure]
    group_element_year_qs = GroupElementYear.objects.filter(pk__in=group_element_year_ids)
    return {
        '_'.join([str(gey.parent_id), str(gey.child.pk)]): link.factory.get_link(gey)  # TODO: Change when migration is done : child.pk must become child_id
        for gey in group_element_year_qs
    }


def __build_tree(root_node, tree_structure, nodes, links):
    root_node.children = __build_children(root_node, tree_structure, nodes, links)
    tree = EducationGroupProgram(root_node)
    return tree


def __build_children(root, tree_structure, nodes, links):
    children = []

    for child_structure in [structure for structure in tree_structure if structure['parent_id'] == root.pk]:
        child_node = copy.deepcopy(nodes[child_structure['child_id']])
        child_node.path = child_structure['path']
        child_node.children = __build_children(child_node, tree_structure, nodes, links)

        link_node = copy.deepcopy(
            links['_'.join([str(child_structure['parent_id']), str(child_structure['child_id'])])]
        )
        link_node.parent = root
        link_node.child = child_node
        children.append(link_node)
    return children
