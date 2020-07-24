from base.models.enums.education_group_types import GroupType, TrainingType


class GroupTypeConverter:
    regex = '\w+'

    def to_python(self, value):
        if value not in GroupType.get_names():
            raise ValueError("%s value: is not a valid group type")
        return value

    def to_url(self, value):
        return value


class TrainingTypeConverter:
    regex = '\w+'

    def to_python(self, value):
        if value not in TrainingType.get_names():
            raise ValueError("%s value: is not a valid training type")
        return value

    def to_url(self, value):
        return value
