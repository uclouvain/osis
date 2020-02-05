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
    level = MessageLevel.ERROR.name

    def __init__(self, message: str, level: MessageLevel = None):
        self.message = message
        self.level = level

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.message
        return other.message == self.message


class BusinessValidator(ABC):

    _messages = None

    def __init__(self, *args, **kwargs):
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
        # TODO :: quid de la responsabilité des succes messages? Qui s'en occupe?
        return [msg for msg in self.messages if msg.level == MessageLevel.SUCCESS]

    def is_valid(self) -> bool:
        self.validate()  # TODO :: utiliser _validation_done attr?
        return not self.error_messages

    def add_message(self, msg: BusinessValidationMessage):
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
        self.validator_args = validator_args
        self.validator_kwargs = validator_kwargs

    def validate(self):
        for validator_class in self.validators:
            validator = validator_class(*self.validator_args, **self.validator_kwargs)
            validator.validate()
            self.add_messages(validator.messages)
