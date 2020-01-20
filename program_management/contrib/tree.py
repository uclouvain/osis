from typing import List

from django.db.models import Model

from base.models.group_element_year import GroupElementYear
from program_management.contrib.mixins import FetchedBusinessObject
from program_management.contrib import node, link
from program_management.models.element import Element


class EducationGroupVersion(Model):
    pass


class EducationGroupProgram(FetchedBusinessObject):
    root_group: node.Node = None

    def __init__(self, pk: int = None):
        super(EducationGroupProgram, self).__init__(pk=pk)

    def fetch(self):
        self = fetch(self.pk_value)



class EducationGroupProgramList:

    @staticmethod
    def get_queryset():
        return []

    @staticmethod
    def get_list() -> List[EducationGroupProgram]:
        result = []
        for obj in EducationGroupProgramList.get_queryset():
            result.append(EducationGroupProgram(obj))
        return result


class EducationGroupProgramVersion(EducationGroupProgram):
    version: EducationGroupVersion = None


def fetch(tree_root_id):
    root_node = node.factory.get_node(
        Element.objects.get(education_group_year_id=tree_root_id)
        # TODO: Change when migration is done : Element.objects.get(group_year_id=tree_root_id)
    )

    structure = GroupElementYear.objects.get_adjacency_list([root_node.pk])
    nodes = __fetch_tree_nodes(structure)
    links = __fetch_tree_links(structure)
    return __build_tree(root_node, structure, nodes, links)


def __fetch_tree_nodes(tree_structure):
    element_ids = [ link['child_id'] for link in tree_structure ]
    element_qs = Element.objects.filter(pk__in=element_ids).select_related(
        'education_group_year',
        'group_year',
        'learning_unit_year',
        'learning_class_year'
    )
    return {element.pk: node.factory.get_node(element) for element in element_qs}

def __fetch_tree_links(tree_structure):
    group_element_year_ids = [ link['id'] for link in tree_structure ]
    group_element_year_qs = GroupElementYear.objects.filter(pk__in=group_element_year_ids)
    return {'_'.join([gey.parent_id, gey.child.pk]) : link.factory.get_link(gey) for gey in group_element_year_qs}  # TODO: Change when migration is done : child.pk must become child_id


def __build_tree(root_node, tree_structure, nodes, links):
    tree = EducationGroupProgram(pk=root_node.pk)
    tree.root_group = root_node
    tree.children = __build_children(root_node, tree_structure, nodes, links)
    return tree

def __build_children(root, tree_structure, nodes, links):
    children = []

    for child_structure in [structure for structure in tree_structure if structure['parent_id'] == root.pk]:
        child_node = nodes[child_structure['child_id']]
        child_node.children = __build_children(child_node, tree_structure, nodes, links)

        link_node = links['_'.join([child_structure['parent_id'], child_structure['child_id']])]
        link_node.parent = root
        link_node.child = child_node
        children.append(link_node)
    return children
