from abc import ABC
from enum import Enum
from typing import List

from django.db.models import Model, QuerySet

from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear


class EducationGroupVersion(models.Model):
    pass


class NodeLink:
    node: Node = None
    link: Link = None


class Node(ABC):
    children: List[NodeLink] = None

    def save(self):
        raise NotImplementedError()


class NodeGroupYear(Node):
    attrs = None


class NodeLearningUnitYear(Node):
    attrs = None


class NodeLearningClassYear(Node):
    attrs = None


class EducationGroupProgram:
    root_group: Node = None
    attrs = None  # From EducationGroupYear (Offre)
    fields: dict = {
        EducationGroupYear: ('acronym',)
    }
    _pk: int = None
    _initial_data: dict = None

    def __init__(self, pk: int = None, initial_data: dict = None):
        self._pk = pk
        self._initial_data = initial_data or self.fetch()
        self.root_group = Node(self._initial_data)

        for key, value in self._initial_data.items():
            if hasattr()
            setattr(self, key, value)

    def fetch(self) -> dict:
        if self._pk:
            return QuerySet.values().get()
        return {}


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


class MessageLevel(Enum):
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    SUCCESS = "succes"

    # Se baser sur le Message level de python


class BusinessValidationMessage:
    message: str = None
    level: MessageLevel = None


class BusinessValidationMixin:

    _messages: List[BusinessValidationMessage] = None

    def __init__(self):
        self._messages = []

    @property
    def messages(self) -> List[BusinessValidationMessage]:
        return self._messages

    def is_valid(self) -> bool:
        return True

    def add_message(self, msg: BusinessValidationMessage):
        self._messages.append(msg)


class PersistBusinessObject(ABC):
    __instances: List[Model] = None

    def __init__(self):
        self.__instances = []

    def save(self):
        for obj in self.__instances:
            obj.save()

    def __setattr__(self, key, value):
        raise NotImplementedError()


class Link(PersistBusinessObject):
    attrs = None  # From GroupElementYear
    __instance: GroupElementYear = None

    def __init__(self, pk: int = None):
        self.__pk = pk

    @property
    def instance(self) -> GroupElementYear:
        if not self.__instance:
            if self.__pk:
                self.__instance = GroupElementYear.objects.get(self.__pk)
            else:
                self.__instance = GroupElementYear()
        return self.__instance

    @property
    def relative_credits(self) -> int:
        return self.instance.relative_credits

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise AttributeError()
        setattr(self.instance, key, value)