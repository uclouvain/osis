from django.utils.translation.trans_null import ngettext_lazy

from osis_common.ddd.interface import BusinessException
from django.utils.translation import gettext_lazy as _


class TrainingNotFoundException(Exception):
    pass


class GroupNotFoundException(Exception):
    pass


class GroupCodeAlreadyExistException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Code already exists")
        super().__init__(message, **kwargs)


class AcademicYearNotFound(Exception):
    pass


class TypeNotFound(Exception):
    pass


class ManagementEntityNotFound(Exception):
    pass


class TeachingCampusNotFound(Exception):
    pass


class ContentConstraintTypeMissing(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("You should precise constraint type")
        super().__init__(message, **kwargs)


class ContentConstraintMinimumMaximumMissing(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("You should precise at least minimum or maximum constraint")
        super().__init__(message, **kwargs)


class ContentConstraintMaximumShouldBeGreaterOrEqualsThanMinimum(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("%(max)s must be greater or equals than %(min)s") % {
                    "max": _("maximum constraint").title(),
                    "min": _("minimum constraint").title(),
                 }
        super().__init__(message, **kwargs)


class CreditShouldBeGreaterOrEqualsThanZero(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Credits must be greater or equals than 0")
        super().__init__(message, **kwargs)


class TrainingHaveEnrollments(BusinessException):
    def __init__(self, *args, enrollment_count=None, **kwargs):
        message = ngettext_lazy(
            "%(count_enrollment)d student is enrolled in the training.",
            "%(count_enrollment)d students are enrolled in the training.",
            enrollment_count
        ) % {"count_enrollment": enrollment_count}
        super().__init__(message, **kwargs)


class TrainingHaveLinkWithEPC(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Linked with EPC")
        super().__init__(message, **kwargs)


class MiniTrainingHaveEnrollments(BusinessException):
    def __init__(self, *args, enrollment_count=None, **kwargs):
        message = ngettext_lazy(
            "%(count_enrollment)d student is enrolled in the mini-training.",
            "%(count_enrollment)d students are enrolled in the mini-training.",
            enrollment_count
        ) % {"count_enrollment": enrollment_count}
        super().__init__(message, **kwargs)


class MiniTrainingHaveLinkWithEPC(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Linked with EPC")
        super().__init__(message, **kwargs)
