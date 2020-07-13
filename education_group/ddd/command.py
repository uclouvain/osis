##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from _decimal import Decimal
from typing import List, Tuple, Optional

import attr

from osis_common.ddd import interface

DecreeName = str
DomainCode = str
CampusName = str
UniversityName = str
PartnerName = str
AimCode = int
AimSection = int


class CreateTrainingCommand(interface.CommandRequest):
    def __init__(
            self,
            abbreviated_title: str,
            status: str,
            code: str,
            year: int,
            type: str,
            credits: Decimal,
            schedule_type: str,
            duration: int,
            start_year: int,

            title_fr: str,
            partial_title_fr: Optional[str],
            title_en: Optional[str],
            partial_title_en: Optional[str],

            keywords: Optional[str],
            internship: Optional[str],
            is_enrollment_enabled: Optional[bool],
            has_online_re_registration: Optional[bool],
            has_partial_deliberation: Optional[bool],
            has_admission_exam: Optional[bool],
            has_dissertation: Optional[bool],
            produce_university_certificate: Optional[bool],
            decree_category: Optional[str],
            rate_code: Optional[str],
            main_language: Optional[str],
            english_activities: Optional[str],
            other_language_activities: Optional[str],
            internal_comment: Optional[str],
            main_domain_code: Optional[str],
            main_domain_decree: Optional[str],

            secondary_domains: Optional[List[Tuple[DecreeName, DomainCode]]],

            isced_domain_code: Optional[str],
            management_entity_acronym: Optional[str],
            administration_entity_acronym: Optional[str],
            end_year: Optional[int],

            teaching_campus_name: Optional[str],
            teaching_campus_organization_name: Optional[str],

            enrollment_campus_name: Optional[str],
            enrollment_campus_organization_name: Optional[str],

            other_campus_activities: Optional[str],

            can_be_funded: Optional[bool],
            funding_orientation: Optional[str],
            can_be_international_funded: Optional[bool],
            international_funding_orientation: Optional[str],

            ares_code: Optional[int],
            ares_graca: Optional[int],
            ares_authorization: Optional[int],

            code_inter_cfb: Optional[str],
            coefficient: Optional[Decimal],

            academic_type: Optional[str],
            duration_unit: Optional[str],

            leads_to_diploma: Optional[bool],
            printing_title: Optional[str],
            professional_title: Optional[str],
            aims: Optional[List[Tuple[AimCode, AimSection]]],

            constraint_type: Optional[str],
            min_constraint: Optional[int],
            max_constraint: Optional[int],
            remark_fr: Optional[str],
            remark_en: Optional[str],
    ):
        self.abbreviated_title = abbreviated_title
        self.status = status
        self.code = code
        self.year = year
        self.type = type
        self.credits = credits
        self.schedule_type = schedule_type
        self.duration = duration
        self.start_year = start_year
        self.title_fr = title_fr
        self.partial_title_fr = partial_title_fr
        self.title_en = title_en
        self.partial_title_en = partial_title_en
        self.keywords = keywords
        self.internship = internship
        self.is_enrollment_enabled = is_enrollment_enabled
        self.has_online_re_registration = has_online_re_registration
        self.has_partial_deliberation = has_partial_deliberation
        self.has_admission_exam = has_admission_exam
        self.has_dissertation = has_dissertation
        self.produce_university_certificate = produce_university_certificate
        self.decree_category = decree_category
        self.rate_code = rate_code
        self.main_language = main_language
        self.english_activities = english_activities
        self.other_language_activities = other_language_activities
        self.internal_comment = internal_comment
        self.main_domain_code = main_domain_code
        self.main_domain_decree = main_domain_decree
        self.secondary_domains = secondary_domains
        self.isced_domain_code = isced_domain_code
        self.management_entity_acronym = management_entity_acronym
        self.administration_entity_acronym = administration_entity_acronym
        self.end_year = end_year
        self.teaching_campus_name = teaching_campus_name
        self.teaching_campus_organization_name = teaching_campus_organization_name
        self.enrollment_campus_name = enrollment_campus_name
        self.enrollment_campus_organization_name = enrollment_campus_organization_name
        self.other_campus_activities = other_campus_activities
        self.can_be_funded = can_be_funded
        self.funding_orientation = funding_orientation
        self.can_be_international_funded = can_be_international_funded
        self.international_funding_orientation = international_funding_orientation
        self.ares_code = ares_code
        self.ares_graca = ares_graca
        self.ares_authorization = ares_authorization
        self.code_inter_cfb = code_inter_cfb
        self.coefficient = coefficient
        self.academic_type = academic_type
        self.duration_unit = duration_unit
        self.leads_to_diploma = leads_to_diploma
        self.printing_title = printing_title
        self.professional_title = professional_title
        self.aims = aims
        self.constraint_type = constraint_type
        self.min_constraint = min_constraint
        self.max_constraint = max_constraint
        self.remark_fr = remark_fr
        self.remark_en = remark_en


class GetGroupCommand(interface.CommandRequest):
    def __init__(self, code: str, year: int):
        self.code = code
        self.year = year


class CreateOrphanGroupCommand(interface.CommandRequest):
    def __init__(
            self,
            code: str,
            year: int,
            type: str,
            abbreviated_title: str,
            title_fr: str,
            title_en: str,
            credits: int,
            constraint_type: str,
            min_constraint: int,
            max_constraint: int,
            management_entity_acronym: str,
            teaching_campus_name: str,
            organization_name: str,
            remark_fr: str,
            remark_en: str,
            start_year: int,
            end_year: Optional[int] = None
    ):
        self.code = code
        self.year = year
        self.type = type
        self.abbreviated_title = abbreviated_title
        self.title_fr = title_fr
        self.title_en = title_en
        self.credits = credits
        self.constraint_type = constraint_type
        self.min_constraint = min_constraint
        self.max_constraint = max_constraint
        self.management_entity_acronym = management_entity_acronym
        self.teaching_campus_name = teaching_campus_name
        self.organization_name = organization_name
        self.remark_fr = remark_fr
        self.remark_en = remark_en
        self.start_year = start_year
        self.end_year = end_year


class CopyGroupCommand(interface.CommandRequest):
    def __init__(self, from_code: str, from_year: int, to_year: int):
        self.from_code = from_code
        self.from_year = from_year
        self.to_year = to_year


@attr.s(frozen=True, slots=True)
class PostponeTrainingCommand(interface.CommandRequest):
    acronym = attr.ib(type=str)
    postpone_from_year = attr.ib(type=int)
    postpone_until_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CopyTrainingToNextYearCommand(interface.CommandRequest):
    acronym = attr.ib(type=str)
    postpone_from_year = attr.ib(type=int)
