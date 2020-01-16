from typing import List, Dict, Set

from django.db.models import Model, QuerySet

from base.models.education_group_year import EducationGroupYear
from program_management.contrib.mixins import FetchedBusinessObject
from program_management.contrib.node import Node


class EducationGroupVersion(Model):
    pass


class EducationGroupProgram(FetchedBusinessObject):
    root_group: Node = None

    def __init__(self, pk: int = None):
        super(EducationGroupProgram, self).__init__(pk=pk)

    def fetch(self):
        pass


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
