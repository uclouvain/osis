from abc import ABC
from enum import Enum
from typing import List


# TODO :: déplacer dans un autre dossier
class MessageLevel(Enum):
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    SUCCESS = "succes"

    # Se baser sur le Message level de python


class BusinessValidationMessage:
    message = None
    level = MessageLevel.ERROR

    def __init__(self, message: str, level: MessageLevel = None):
        self.message = message
        self.level = level

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.message
        return other.message == self.message

    def __str__(self):
        return "%(level)s %(msg)s" % {'level': self.level, 'msg': self.message}


class BusinessValidator(ABC):

    _messages = None

    success_messages = None

    def __init__(self, *args, **kwargs):
        self._messages = []

    @property
    def messages(self) -> List[BusinessValidationMessage]:
        return self._messages + (self.success_messages or [])

    @property
    def error_messages(self) -> List[BusinessValidationMessage]:
        return [msg for msg in self.messages if msg.level == MessageLevel.ERROR]

    @property
    def warning_messages(self) -> List[BusinessValidationMessage]:
        return [msg for msg in self.messages if msg.level == MessageLevel.WARNING]

    def is_valid(self) -> bool:
        self.validate()  # TODO :: utiliser _validation_done attr?
        return not self.error_messages

    def add_message(self, msg: BusinessValidationMessage):
        assert msg.level != MessageLevel.SUCCESS, "please redefine the 'success_messages' property instead"
        self._messages.append(msg)

    def add_error_message(self, msg: str):
        self._messages.append(BusinessValidationMessage(msg, level=MessageLevel.ERROR))

    def add_messages(self, messages: List[BusinessValidationMessage]):
        for msg in messages:
            self.add_message(msg)

    def validate(self, *args, **kwargs):
        """Method used to add messages during validation"""
        raise NotImplementedError()


class BusinessListValidator(BusinessValidator):
    validators = None

    validator_args = None
    validator_kwargs = None

    def __init__(self, validator_args=None, validator_kwargs=None):
        super(BusinessListValidator, self).__init__()
        assert self.success_messages, "Please set the 'success_messages' attribute"
        self.validator_args = validator_args
        self.validator_kwargs = validator_kwargs or {}

    def validate(self):
        for validator_class in self.validators:
            validator = validator_class(*self.validator_args, **self.validator_kwargs)
            validator.validate()
            self.add_messages(validator.messages)
