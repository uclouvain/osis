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
from typing import List, TypeVar

from base.models.enums.academic_type import AcademicTypes
from base.models.enums.activity_presence import ActivityPresence
from base.models.enums.decree_category import DecreeCategories
from base.models.enums.duration_unit import DurationUnitsEnum
from base.models.enums.education_group_types import TrainingType
from base.models.enums.funding_codes import FundingCodes
from base.models.enums.internship_presence import InternshipPresence
from base.models.enums.rate_code import RateCode
from base.models.enums.schedule_type import ScheduleTypeEnum
from base.models.utils.utils import ChoiceEnum
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._co_graduation import CoGraduation
from education_group.ddd.domain._co_organization import Coorganization
from education_group.ddd.domain._diploma import Diploma, DiplomaAim
from education_group.ddd.domain._entity import Entity
from education_group.ddd.domain._funding import Funding
from education_group.ddd.domain._hops import HOPS
from education_group.ddd.domain._isced_domain import IscedDomain, IscedDomainIdentity
from education_group.ddd.domain._language import Language
from education_group.ddd.domain._study_domain import StudyDomain
from education_group.ddd.domain._titles import Titles
from osis_common.ddd import interface

from education_group.ddd.business_types import *


class TrainingIdentity(interface.EntityIdentity):
    def __init__(self, acronym: str, year: int):
        self.acronym = acronym
        self.year = year

    def __hash__(self):
        return hash(self.acronym + str(self.year))

    def __eq__(self, other):
        return self.acronym == other.acronym and self.year == other.year


class TrainingBuilder:
    def get_training(self, command: 'CreateTrainingCommand') -> 'Training':
        training_identity = TrainingIdentity(command.abbreviated_title, command.year)
        secondary_domains = []
        for dom in command.secondary_domains:
            secondary_domains.append(
                StudyDomain(
                    entity_id=StudyDomainIdentity(dom[0], dom[1]),
                    domain_name=None,
                )
            )

        command_aims = []
        for aim in command.aims:
            DiplomaAim(
                entity_id=DiplomaAimIdentity(code=aim[0], section=aim[1]),
                description=None,  # FIXME :: Training() object should receive entity_id instead of Object? And lazy load the DiplomaAim objects?
            )

        return Training(
            entity_identity=training_identity,
            type=self._get_enum_from_str(command.type, TrainingType),
            credits=command.credits,
            schedule_type=self._get_enum_from_str(command.schedule_type, ScheduleTypeEnum),
            duration=command.duration,
            duration_unit=self._get_enum_from_str(command.duration_unit, DurationUnitsEnum),
            start_year=command.start_year,
            titles=Titles(
                title_fr=command.title_fr,
                partial_title_fr=command.partial_title_fr,
                title_en=command.title_en,
                partial_title_en=command.partial_title_en,
            ),
            keywords=command.keywords,
            internship=self._get_enum_from_str(command.internship, InternshipPresence),
            is_enrollment_enabled=command.is_enrollment_enabled,
            has_online_re_registration=command.has_online_re_registration,
            has_partial_deliberation=command.has_partial_deliberation,
            has_admission_exam=command.has_admission_exam,
            has_dissertation=command.has_dissertation,
            produce_university_certificate=command.produce_university_certificate,
            decree_category=self._get_enum_from_str(command.decree_category, DecreeCategories),
            rate_code=self._get_enum_from_str(command.rate_code, RateCode),
            main_language=Language(command.main_language) if command.main_language else None,
            english_activities=self._get_enum_from_str(command.english_activities, ActivityPresence),
            other_language_activities=self._get_enum_from_str(command.other_language_activities, ActivityPresence),
            internal_comment=command.internal_comment,
            main_domain=StudyDomain(
                entity_id=StudyDomainIdentity(decree_name=command.main_domain_decree, code=command.main_domain_code),
                domain_name=None,
            ),
            secondary_domains=secondary_domains,
            isced_domain=IscedDomain(
                entity_id=IscedDomainIdentity(command.isced_domain_code),
                title_fr=None,
                title_en=None,
            ),
            management_entity=Entity(acronym=command.management_entity_acronym),
            administration_entity=Entity(acronym=command.administration_entity_acronym),
            end_year=command.end_year,
            teaching_campus=Campus(
                name=command.teaching_campus_name,
                university_name=command.teaching_campus_organization_name,
            ),
            enrollment_campus=Campus(
                name=command.enrollment_campus_name,
                university_name=command.enrollment_campus_organization_name,
            ),
            other_campus_activities=self._get_enum_from_str(command.other_campus_activities, ActivityPresence),
            funding=Funding(
                can_be_funded=command.can_be_funded,
                funding_orientation=command.funding_orientation,
                can_be_international_funded=command.can_be_international_funded,
                international_funding_orientation=FundingCodes[
                    command.international_funding_orientation
                ] if command.international_funding_orientation else None,
            ),
            hops=HOPS(
                ares_code=command.ares_code,
                ares_graca=command.ares_graca,
                ares_authorization=command.ares_authorization,
            ),
            co_graduation=CoGraduation(
                code_inter_cfb=command.code_inter_cfb,
                coefficient=command.coefficient,
            ),
            academic_type=self._get_enum_from_str(command.academic_type, AcademicTypes),
            diploma=Diploma(
                leads_to_diploma=command.leads_to_diploma,
                printing_title=command.printing_title,
                professional_title=command.professional_title,
                aims=command_aims,
            ),
        )

    def _get_enum_from_str(self, value: str, enum_class):
        if value is None:
            return None
        try:
            return enum_class[value]
        except ValueError:
            raise interface.BusinessException(
                "Invalid enum choice (value={}, enumeration_class={})".format(value, enum_class)
            )


class Training(interface.RootEntity):

    # FIXME :: split into ValueObjects (to discuss with business people)
    def __init__(
            self,
            entity_identity: 'TrainingIdentity',
            type: TrainingType,
            credits: Decimal,
            schedule_type: ScheduleTypeEnum,
            duration: int,
            start_year: int,
            titles: Titles,
            keywords: str = None,
            internship: InternshipPresence = None,
            is_enrollment_enabled: bool = True,
            has_online_re_registration: bool = True,
            has_partial_deliberation: bool = False,
            has_admission_exam: bool = False,
            has_dissertation: bool = False,
            produce_university_certificate: bool = False,
            decree_category: DecreeCategories = None,
            rate_code: RateCode = None,
            main_language: Language = None,
            english_activities: ActivityPresence = None,
            other_language_activities: ActivityPresence = None,
            internal_comment: str = None,
            main_domain: StudyDomain = None,
            secondary_domains: List[StudyDomain] = None,
            isced_domain: IscedDomain = None,
            management_entity: Entity = None,
            administration_entity: Entity = None,
            end_year: int = None,
            teaching_campus: Campus = None,
            enrollment_campus: Campus = None,
            other_campus_activities: ActivityPresence = None,
            funding: Funding = None,
            hops: HOPS = None,
            co_graduation: CoGraduation = None,
            co_organizations: List[Coorganization] = None,
            academic_type: AcademicTypes = None,
            duration_unit: DurationUnitsEnum = None,
            diploma: Diploma = None,
    ):
        super(Training, self).__init__(entity_id=entity_identity)
        self.entity_id = entity_identity
        self.type = type
        self.credits = credits
        self.schedule_type = schedule_type
        self.duration = duration
        self.duration_unit = duration_unit or DurationUnitsEnum.QUADRIMESTER
        self.start_year = start_year
        self.titles = titles
        self.keywords = keywords
        self.internship = internship
        self.is_enrollment_enabled = is_enrollment_enabled or True
        self.has_online_re_registration = has_online_re_registration or True
        self.has_partial_deliberation = has_partial_deliberation or False
        self.has_admission_exam = has_admission_exam or False
        self.has_dissertation = has_dissertation or False
        self.produce_university_certificate = produce_university_certificate or False
        self.decree_category = decree_category
        self.rate_code = rate_code
        self.main_language = main_language
        self.english_activities = english_activities
        self.other_language_activities = other_language_activities
        self.internal_comment = internal_comment
        self.main_domain = main_domain
        self.secondary_domains = secondary_domains
        self.isced_domain = isced_domain
        self.management_entity = management_entity
        self.administration_entity = administration_entity
        self.end_year = end_year
        self.teaching_campus = teaching_campus
        self.enrollment_campus = enrollment_campus
        self.other_campus_activities = other_campus_activities
        self.funding = funding
        self.hops = hops
        self.co_graduation = co_graduation
        self.co_organizations = co_organizations
        self.academic_type = academic_type
        self.diploma = diploma

    @property
    def acronym(self) -> str:
        return self.entity_id.acronym

    @property
    def year(self) -> int:
        return self.entity_id.year

    def is_finality(self) -> bool:
        return self.type in set(TrainingType.finality_types_enum())

    def is_bachelor(self) -> bool:
        return self.type == TrainingType.BACHELOR

    def is_master_specialized(self):
        return self.type == TrainingType.MASTER_MC

    def is_aggregation(self):
        return self.type == TrainingType.AGGREGATION

    def is_master_60_credits(self):
        return self.type == TrainingType.MASTER_M1

    def is_master_120_credits(self):
        return self.type == TrainingType.PGRM_MASTER_120

    def is_master_180_240_credits(self):
        return self.type == TrainingType.PGRM_MASTER_180_240
