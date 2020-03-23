import itertools
from typing import List

from base.models import education_group_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import EducationGroupTypesEnum, TrainingType, MiniTrainingType
from base.models import learning_unit_year
from program_management.ddd.repositories import load_tree, load_node


def find_roots(
        objects,
        parents_as_instances=False,
        with_parents_of_parents=False,
        root_types: List[EducationGroupTypesEnum] = None
):
    _assert_same_academic_year(objects)
    _assert_same_objects_class(objects)

    default_root_types = set(TrainingType) | set(MiniTrainingType) - {MiniTrainingType.OPTION}
    root_types = default_root_types | set(root_types or [])

    child_branch_ids = [obj.id for obj in objects if isinstance(obj, EducationGroupYear)]
    child_leaf_ids = [obj.id for obj in objects if isinstance(obj, learning_unit_year.LearningUnitYear)]
    trees = load_tree.load_trees_from_children(child_branch_ids=child_branch_ids, child_leaf_ids=child_leaf_ids)

    nodes = [load_node.load_node_learning_unit_year(obj_id) for obj_id in child_leaf_ids]
    nodes += [load_node.load_node_education_group_year(obj_id) for obj_id in child_branch_ids]

    parents_by_children_id = _get_parents_for_nodes(nodes, trees, root_types)

    if with_parents_of_parents:
        flat_list_of_parents = _flatten_list_of_lists(parents_by_children_id.values())
        parents_of_parents = _get_parents_for_nodes(flat_list_of_parents, trees, root_types)
        parents_by_children_id.update(parents_of_parents)

    result = {}
    for key, value in parents_by_children_id.items():
        result[key] = [node.node_id for node in value]

    if parents_as_instances:
        result = _convert_parent_ids_to_instances(result)
    return result


def _get_parents_for_nodes(nodes, trees, is_root_when_matches):
    parents = {}
    for node in nodes:
        node_parents = itertools.chain.from_iterable(
            [tree.get_first_ancestors_matching_type(node, is_root_when_matches) for tree in trees]
        )
        parents[node.node_id] = set(node_parents)
    return parents


def _flatten_list_of_lists(list_of_lists):
    return list(set(itertools.chain.from_iterable(list_of_lists)))


def _convert_parent_ids_to_instances(root_ids_by_object_id):
    flat_root_ids = _flatten_list_of_lists(root_ids_by_object_id.values())
    map_instance_by_id = {obj.id: obj for obj in education_group_year.search(id=flat_root_ids)}
    return {
        obj_id: sorted([map_instance_by_id[parent_id] for parent_id in parents], key=lambda obj: obj.acronym)
        for obj_id, parents in root_ids_by_object_id.items()
    }


def _assert_same_objects_class(objects):
    if not objects:
        return
    first_obj = objects[0]
    obj_class = first_obj.__class__
    if obj_class not in (learning_unit_year.LearningUnitYear, EducationGroupYear):
        raise AttributeError("Objects must be either LearningUnitYear or EducationGroupYear instances.")
    if any(obj for obj in objects if obj.__class__ != obj_class):
        raise AttributeError("All objects must be the same class instance ({})".format(obj_class))


def _assert_same_academic_year(objects):
    if len(set(getattr(obj, 'academic_year_id') for obj in objects)) > 1:
        raise AttributeError(
            "The algorithm should load only graph/structure for 1 academic_year "
            "to avoid too large 'in-memory' data and performance issues."
        )