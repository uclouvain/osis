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
from typing import List, Tuple

from osis_common.ddd import interface
from education_group.ddd.business_types import *


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
            acronym: str,
            year: int,
            type: str,
            credits: Decimal,
            schedule_type: str,
            duration: int,
            start_year: int,

            title_fr: str,
            partial_title_fr: str = None,
            title_en: str = None,
            partial_title_en: str = None,

            keywords: str = None,
            internship: str = None,
            is_enrollment_enabled: bool = True,
            has_online_re_registration: bool = True,
            has_partial_deliberation: bool = False,
            has_admission_exam: bool = False,
            has_dissertation: bool = False,
            produce_university_certificate: bool = False,
            decree_category: str = None,
            rate_code: str = None,
            main_language: str = None,
            english_activities: str = None,
            other_language_activities: str = None,
            internal_comment: str = None,
            main_domain_code: str = None,
            main_domain_decree: str = None,

            secondary_domains: List[Tuple[DecreeName, DomainCode]] = None,

            isced_domain_code: str = None,
            management_entity_acronym: str = None,
            administration_entity_acronym: str = None,
            end_year: int = None,

            teaching_campus: Tuple[CampusName, UniversityName] = None,
            enrollment_campus: Tuple[CampusName, UniversityName] = None,

            other_campus_activities: str = None,

            can_be_funded: bool = False,
            funding_orientation: str = None,
            can_be_international_funded: bool = False,
            international_funding_orientation: str = None,

            ares_code: int = None,
            ares_graca: int = None,
            ares_authorization: int = None,

            code_inter_cfb: str = None,
            coefficient: Decimal = None,

            academic_type: str = None,
            duration_unit: str = None,

            leads_to_diploma: bool = None,
            printing_title: str = None,
            professional_title: str = None,
            aims: List[Tuple[AimCode, AimSection]] = None
    ):
        self.acronym = acronym
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
        self.teaching_campus = teaching_campus
        self.enrollment_campus = enrollment_campus
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
