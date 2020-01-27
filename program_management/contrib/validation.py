from abc import ABC
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


class BusinessValidator(ABC):

    _messages: List[BusinessValidationMessage] = None

    def __init__(self):
        self._messages = []

    @property
    def messages(self) -> List[BusinessValidationMessage]:
        return self._messages

    @property
    def error_messages(self) -> List[BusinessValidationMessage]:
        return [msg for msg in self.messages if msg.level == MessageLevel.ERROR]

    @property
    def warning_messages(self) -> List[BusinessValidationMessage]:
        return [msg for msg in self.messages if msg.level == MessageLevel.WARNING]

    @property
    def success_messages(self):
        return [msg for msg in self.messages if msg.level == MessageLevel.SUCCESS]

    def is_valid(self) -> bool:
        return not self.error_messages

    def add_message(self, msg: BusinessValidationMessage):
        self._messages.append(msg)
