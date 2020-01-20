from abc import ABC
from typing import List

from django.forms import model_to_dict

from base.models.education_group_year import EducationGroupYear
from base.models.learning_unit_year import LearningUnitYear
from education_group.models.group_year import GroupYear
from program_management.contrib.academic_year import AcademicYearBusiness
from program_management.contrib.mixins import PersistentBusinessObject
from program_management.models.element import Element
from program_management.models.enums import node_type


class NodeFactory:
    def get_node(self, element: Element):
        node_cls = {
            node_type.EDUCATION_GROUP: NodeEductionGroupYear,   # TODO: Remove when migration is done

            node_type.GROUP: NodeGroupYear,
            node_type.LEARNING_UNIT: NodeLearningUnitYear,
            node_type.LEARNING_CLASS: NodeLearningClassYear
        }[element.node_type]
        return node_cls(element)


factory = NodeFactory()


class Node(ABC):
    children = None


class NodeEductionGroupYear(Node, PersistentBusinessObject):      # TODO: Remove when migration is done
    map_with_database = {
        EducationGroupYear: {
           'acronym': 'acronym',
           'title': 'title',
            # A Compléter
        }
    }

    def __init__(self, element: Element):
        initial_values = model_to_dict(element.education_group_year)
        super().__init__(initial_values)
        self.pk = element.education_group_year_id  # TODO: Make better than this


class NodeGroupYear(Node, PersistentBusinessObject):
    map_with_database = {
        GroupYear: {
            # à compléter ...
        }
    }


class NodeLearningUnitYear(Node, PersistentBusinessObject):
    map_with_database = {
        LearningUnitYear: {
            'acronym': 'acronym',
            'academic_year_id': 'academic_year_id',
            # à compléter ...
        },
    }

    academic_year = None

    @property
    def year(self):
        return self.academic_year.year


class NodeLearningClassYear(Node, PersistentBusinessObject):
    attrs = None
