from enum import Enum
from typing import List


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
