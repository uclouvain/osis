from abc import ABC
from typing import List, Dict

from django.utils.translation import gettext_lazy as _, ngettext_lazy

from education_group.ddd.business_types import *
from education_group.templatetags.academic_year_display import display_as_academic_year
from osis_common.ddd.interface import BusinessException


class TrainingNotFoundException(Exception):
    def __init__(self, *args, acronym: str = None, year: int = None):
        message = ''
        if acronym or year:
            message = _("Training not found : {acronym} {year}".format(acronym=acronym, year=year))
        super().__init__(message, *args)


class MiniTrainingNotFoundException(Exception):
    pass


class GroupNotFoundException(Exception):
    pass


class CodeAlreadyExistException(BusinessException):
    def __init__(self, year: int, **kwargs):
        message = _("Code already exists in %(academic_year)s") % {"academic_year": display_as_academic_year(year)}
        super().__init__(message, **kwargs)


class GroupIsBeingUsedException(Exception):
    pass


class MiniTrainingIsBeingUsedException(Exception):
    pass


class TrainingAcronymAlreadyExistException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Acronym already exists")
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


class StartYearGreaterThanEndYearException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Validity cannot be greater than last year of organization")
        super().__init__(message, **kwargs)


class CreditShouldBeGreaterOrEqualsThanZero(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Credits must be greater or equals than 0")
        super().__init__(message, **kwargs)


class AcronymRequired(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Acronym/Short title is required")
        super().__init__(message, **kwargs)


class AcronymAlreadyExist(BusinessException):
    def __init__(self, abbreviated_title: str, *args, **kwargs):
        message = _("Acronym/Short title '{}' already exists").format(abbreviated_title)
        super().__init__(message, **kwargs)


class CannotCopyGroupDueToEndDate(BusinessException):
    def __init__(self, group: 'Group', *args, **kwargs):
        message = _(
            "You can't copy the group '{code}' from {from_year} to {to_year} because it ends in {end_year}"
        ).format(
            code=group.code,
            from_year=group.year,
            to_year=group.year + 1,
            end_year=group.end_year,
        )
        super().__init__(message, **kwargs)


class CannotCopyTrainingDueToEndDate(BusinessException):
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


class CannotCopyMiniTrainingDueToEndDate(BusinessException):
    def __init__(self, mini_training: 'MiniTraining', *args, **kwargs):
        message = _(
            "You can't copy the mini-training '{code}' from {from_year} to {to_year} because it ends in {end_year}"
        ).format(
            code=mini_training.code,
            from_year=mini_training.year,
            to_year=mini_training.year + 1,
            end_year=mini_training.end_year,
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


class TrainingHaveEnrollments(BusinessException):
    def __init__(self, acronym: str, year: int, enrollment_count: int, **kwargs):
        message = ngettext_lazy(
            "%(count_enrollment)d student is enrolled in the training %(acronym)s (%(academic_year)s).",
            "%(count_enrollment)d students are enrolled in the training %(acronym)s (%(academic_year)s).",
            enrollment_count
        ) % {"count_enrollment": enrollment_count, "acronym": acronym, "academic_year": display_as_academic_year(year)}
        super().__init__(message, **kwargs)


class TrainingHaveLinkWithEPC(BusinessException):
    def __init__(self, acronym, year, **kwargs):
        message = _("The training {acronym} ({academic_year}) have links in EPC application").format(
            acronym=acronym,
            academic_year=display_as_academic_year(year)
        )
        super().__init__(message, **kwargs)


class MiniTrainingHaveEnrollments(BusinessException):
    def __init__(self, abbreviated_title: str, year: int, enrollment_count: int, **kwargs):
        message = ngettext_lazy(
            "%(count_enrollment)d student is enrolled in the mini-training %(abbreviated_title)s (%(academic_year)s).",
            "%(count_enrollment)d students are enrolled in the mini-training %(abbreviated_title)s "
            "(%(academic_year)s).",
            enrollment_count
        ) % {
            "count_enrollment": enrollment_count,
            "abbreviated_title": abbreviated_title,
            "academic_year": display_as_academic_year(year),
        }
        super().__init__(message, **kwargs)


class MiniTrainingHaveLinkWithEPC(BusinessException):
    def __init__(self, abbreviated_title: str, year: int, **kwargs):
        message = _("The mini-training {abbreviated_title} ({academic_year}) have links in EPC application").format(
            abbreviated_title=abbreviated_title,
            academic_year=display_as_academic_year(year)
        )
        super().__init__(message, **kwargs)


class VersionNameAlreadyExist(BusinessException):
    def __init__(self, version_name: str, *args, **kwargs):
        message = _("Version name {} already exists").format(version_name)
        super().__init__(message, **kwargs)


class MultipleEntitiesFoundException(BusinessException):
    def __init__(self, entity_acronym: str, year: int, *args, **kwargs):
        message = _(
            "Multiple entities {entity_acronym} found in {year}"
        ).format(entity_acronym=entity_acronym, year=year)
        super().__init__(message, **kwargs)


class AbstractConsistencyException(ABC):
    def __init__(self, year_to: int, conflict_fields: List[str], *args, **kwargs):
        fields_str = ", ".join([str(self.__map_field_to_label(field_name)) for field_name in conflict_fields])
        message = _("Consistency error in %(academic_year)s: %(fields)s has already been modified") % {
            "academic_year": display_as_academic_year(year_to),
            "fields": fields_str
        }
        self.conflicted_fields_year = year_to
        super().__init__(message, **kwargs)

    def __map_field_to_label(self, field_name: str) -> str:
        return {
            "credits": _("Credits"),
            "titles": _("Titles"),
            "status": _("Status"),
            "schedule_type": _("Schedule type"),
            "duration": _("Duration"),
            "duration_unit": _("duration unit"),
            "keywords": _("Keywords"),
            "internship_presence": _("Internship"),
            "is_enrollment_enabled": _("Enrollment enabled"),
            "has_online_re_registration": _("Web re-registration"),
            "has_partial_deliberation": _("Partial deliberation"),
            "has_admission_exam": _("Admission exam"),
            "has_dissertation": _("dissertation"),
            "produce_university_certificate": _("University certificate"),
            "decree_category": _("Decree category"),
            "rate_code": _("Rate code"),
            "main_language": _("Primary language"),
            "english_activities": _("activities in English").capitalize(),
            "other_language_activities": _("Other languages activities"),
            "internal_comment": _("comment (internal)").capitalize(),
            "main_domain": _("main domain"),
            "secondary_domains": _("secondary domains"),
            "isced_domain": _("ISCED domain"),
            "management_entity": _("Management entity"),
            "administration_entity": _("Administration entity"),
            "teaching_campus": _("Learning location"),
            "enrollment_campus": _("Enrollment campus"),
            "other_campus_activities": _("Activities on other campus"),
            "funding": _("Funding"),
            "hops": _("hops"),
            "co_graduation": _("co-graduation"),
            "academic_type": _("Academic type"),
            "diploma": _("Diploma"),
            "content_constraint": _("Content constraint"),
            "remark": _("Remark"),
            "professional_title": _("Professionnal title"),
            "printing_title": _('Diploma title'),
            "leads_to_diploma": _('Leads to diploma/certificate'),
            "certificate_aims": _("certificate aims"),
        }.get(field_name, field_name)


class GroupCopyConsistencyException(AbstractConsistencyException, BusinessException):
    pass


class TrainingCopyConsistencyException(AbstractConsistencyException, BusinessException):
    pass


class MiniTrainingCopyConsistencyException(AbstractConsistencyException, BusinessException):
    pass


class CertificateAimsCopyConsistencyException(AbstractConsistencyException, BusinessException):
    pass


class HopsDataShouldBeGreaterOrEqualsThanZeroAndLessThan9999(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("The fields concerning ARES must be greater than or equal to 1 and less than or equal to 9999")
        super().__init__(message, **kwargs)


class HopsFieldsAllOrNone(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _('The fields concerning ARES have to be ALL filled-in or none of them')
        super().__init__(message, **kwargs)


class AresCodeShouldBeGreaterOrEqualsThanZeroAndLessThan9999(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("The fields concerning ARES must be greater than or equal to 1 and less than or equal to 9999")
        super().__init__(message, **kwargs)


class AresGracaShouldBeGreaterOrEqualsThanZeroAndLessThan9999(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "The fields concerning ARES must be greater than or equal to 1 and less than or equal to 9999")
        super().__init__(message, **kwargs)


class AresAuthorizationShouldBeGreaterOrEqualsThanZeroAndLessThan9999(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "The fields concerning ARES must be greater than or equal to 1 and less than or equal to 9999")
        super().__init__(message, **kwargs)


class AresDataShouldBeGreaterOrEqualsThanZeroAndLessThan9999(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("The fields concerning ARES must be greater than or equal to 1 and less than or equal to 9999")
        super().__init__(message, **kwargs)
