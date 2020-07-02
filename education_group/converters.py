from base.models.enums.education_group_types import GroupType, MiniTrainingType


class GroupTypeConverter:
    regex = '\w+'

    def to_python(self, value):
        if value not in GroupType.get_names():
            raise ValueError("%s value: is not a valid group type")
        return value

    def to_url(self, value):
        return value


class MiniTrainingTypeConverter:
    regex = '\w+'

    def to_python(self, value):
        if value not in MiniTrainingType.get_names():
            raise ValueError("%s value: is not a valid mini-training type")
        return value

    def to_url(self, value):
        return value
