from abc import ABC
from typing import List

from base.models.learning_unit_year import LearningUnitYear
from education_group.models.group_year import GroupYear
from program_management.contrib.academic_year import AcademicYearBusiness
from program_management.contrib.mixins import PersistentBusinessObject


class Node(ABC):
    children: List[Link] = None


# class NodeLink:
#     node: Node = None
#     children_links: List[Link] = None
#
#
#
# class NodeLink:
#     node: Node = None
#     link: Link = None


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

    academic_year: AcademicYearBusiness = None

    @property
    def year(self):
        return self.academic_year.year


class NodeLearningClassYear(Node, PersistentBusinessObject):
    attrs = None
