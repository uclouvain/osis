from osis_common.ddd.interface import BusinessException
from django.utils.translation import gettext_lazy as _
from education_group.ddd.business_types import *


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


class AcronymRequired(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Acronym/Short title is required")
        super().__init__(message, **kwargs)


class TrainingAcronymAlreadyExist(BusinessException):
    def __init__(self, abbreviated_title: str, *args, **kwargs):
        message = _("Acronym/Short title '{}' already exists").format(abbreviated_title)
        super().__init__(message, **kwargs)


class CannotCopyDueToEndDate(BusinessException):
    def __init__(self, training: 'Training', *args, **kwargs):
        message = _(
            "You can't copy the training '{acronym}' from {from_year} to {to_year} because it ends in {end_year}"
        ).format(
            acronym=training.acronym,
            from_year=training.year,
            to_year=training.year + 1,
            end_year=training.end_year,
        )
        super().__init__(message, **kwargs)


class StartYearGreaterThanEndYear(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _('End year must be greater than the start year, or equal')
        super().__init__(message, **kwargs)


class MaximumCertificateAimType2Reached(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("There can only be one type 2 expectation")
        super().__init__(message, **kwargs)
