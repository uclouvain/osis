##############################################################################
#
#    OSIS stands for Open Student Information System. It"s an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import List

from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from base.models.utils.utils import ChoiceEnum


# TODO :: move the file into the domain ? And rename EducationGroupTypesEnum to NodeTypeEnum
class EducationGroupTypesEnum(ChoiceEnum):
    pass


class TrainingType(EducationGroupTypesEnum):
    AGGREGATION = _("Aggregation")
    CERTIFICATE_OF_PARTICIPATION = _("Certificate of participation")
    CERTIFICATE_OF_SUCCESS = _("Certificate of success")
    CERTIFICATE_OF_HOLDING_CREDITS = _("Certificate of holding credits")
    BACHELOR = _("Bachelor")
    CERTIFICATE = _("Certificate")
    CAPAES = _("CAPAES")
    RESEARCH_CERTIFICATE = _("Research certificate")
    UNIVERSITY_FIRST_CYCLE_CERTIFICATE = _("University first cycle certificate")
    UNIVERSITY_SECOND_CYCLE_CERTIFICATE = _("University second cycle certificate")
    ACCESS_CONTEST = _("Access contest")
    LANGUAGE_CLASS = _("Language classes")
    ISOLATED_CLASS = _("Isolated classes")
    PHD = pgettext_lazy("Ph.D for education group", "Ph.D")
    FORMATION_PHD = _("Formation PhD")
    JUNIOR_YEAR = _("Junior year")
    PGRM_MASTER_120 = _("Program master 120")
    MASTER_MA_120 = _("Master MA 120")
    MASTER_MD_120 = _("Master MD 120")
    MASTER_MS_120 = _("Master MS 120")
    PGRM_MASTER_180_240 = _("Program master 180-240")
    MASTER_MA_180_240 = _("Master MA 180-240")
    MASTER_MD_180_240 = _("Master MD 180-240")
    MASTER_MS_180_240 = _("Master MS 180-240")
    MASTER_M1 = _("Master in 60 credits")
    MASTER_MC = _("Master of specialist")
    INTERNSHIP = pgettext_lazy("Internship for education group", "Internship")

    @classmethod
    def finality_types(cls) -> List[str]:
        return [enum.name for enum in cls.finality_types_enum()]

    @classmethod
    def finality_types_enum(cls) -> List[EducationGroupTypesEnum]:
        return [
            cls.MASTER_MA_120, cls.MASTER_MD_120, cls.MASTER_MS_120,
            cls.MASTER_MA_180_240, cls.MASTER_MD_180_240, cls.MASTER_MS_180_240
        ]

    @classmethod
    def attestation_types(cls):
        return [
            cls.CERTIFICATE_OF_PARTICIPATION.name,
            cls.CERTIFICATE_OF_SUCCESS.name,
            cls.CERTIFICATE_OF_HOLDING_CREDITS.name,
        ]

    @classmethod
    def university_certificate_types(cls):
        return [
            cls.UNIVERSITY_FIRST_CYCLE_CERTIFICATE.name,
            cls.UNIVERSITY_SECOND_CYCLE_CERTIFICATE.name
        ]

    @classmethod
    def continuing_education_types(cls):
        return cls.attestation_types() + cls.university_certificate_types()

    @classmethod
    def root_master_2m_types(cls) -> List[str]:
        return [enum.name for enum in cls.root_master_2m_types_enum()]

    @classmethod
    def root_master_2m_types_enum(cls) -> List[EducationGroupTypesEnum]:
        return [cls.PGRM_MASTER_120, cls.PGRM_MASTER_180_240]

    @classmethod
    def with_diploma_values_set_initially_as_true(cls):
        return [
            cls.AGGREGATION.name, cls.BACHELOR.name, cls.FORMATION_PHD.name, cls.PHD.name, cls.MASTER_MA_120.name,
            cls.MASTER_MD_120.name, cls.MASTER_MS_120.name, cls.MASTER_MA_180_240.name, cls.MASTER_MD_180_240.name,
            cls.MASTER_MS_180_240.name, cls.MASTER_M1.name, cls.MASTER_MC.name
        ]

    @classmethod
    def with_admission_condition(cls):
        return [
            cls.BACHELOR.name,
            cls.MASTER_MC.name,
            cls.MASTER_M1.name,
            cls.PGRM_MASTER_120.name,
            cls.PGRM_MASTER_180_240.name,
            cls.AGGREGATION.name,
            cls.CERTIFICATE.name,
            cls.RESEARCH_CERTIFICATE.name,
            cls.UNIVERSITY_FIRST_CYCLE_CERTIFICATE.name,
            cls.UNIVERSITY_SECOND_CYCLE_CERTIFICATE.name,
            cls.CAPAES.name,
            cls.CERTIFICATE_OF_PARTICIPATION.name,
            cls.CERTIFICATE_OF_SUCCESS.name,
            cls.CERTIFICATE_OF_HOLDING_CREDITS.name
        ]

    @classmethod
    def with_skills_achievements(cls):
        return [
            cls.BACHELOR.name,
            cls.MASTER_MC.name,
            cls.MASTER_M1.name,
            cls.PGRM_MASTER_120.name,
            cls.PGRM_MASTER_180_240.name,
            cls.AGGREGATION.name,
            cls.CERTIFICATE.name,
            cls.RESEARCH_CERTIFICATE.name,
            cls.CERTIFICATE_OF_PARTICIPATION.name,
            cls.CERTIFICATE_OF_HOLDING_CREDITS.name,
            cls.CERTIFICATE_OF_SUCCESS.name,
            cls.UNIVERSITY_FIRST_CYCLE_CERTIFICATE.name,
            cls.UNIVERSITY_SECOND_CYCLE_CERTIFICATE.name
        ]


class MiniTrainingType(EducationGroupTypesEnum):
    DEEPENING = _("Deepening")
    SOCIETY_MINOR = _("Society minor")
    ACCESS_MINOR = _("Access minor")
    OPEN_MINOR = _("Open minor")
    DISCIPLINARY_COMPLEMENT_MINOR = _("Disciplinary complement minor")
    FSA_SPECIALITY = _("FSA speciality")
    OPTION = _("Option")
    MOBILITY_PARTNERSHIP = _("Mobility partnership")

    @classmethod
    def get_eligible_to_be_created(cls) -> List['MiniTrainingType']:
        return [
            cls.DEEPENING,
            cls.SOCIETY_MINOR,
            cls.ACCESS_MINOR,
            cls.OPEN_MINOR,
            cls.DISCIPLINARY_COMPLEMENT_MINOR,
            cls.OPTION
        ]

    @classmethod
    def minors(cls):
        return [
            cls.SOCIETY_MINOR.name, cls.ACCESS_MINOR.name, cls.OPEN_MINOR.name, cls.DISCIPLINARY_COMPLEMENT_MINOR.name
        ]

    @classmethod
    def minors_and_deepening(cls) -> List['MiniTrainingType']:
        return cls.minors_enum() + [cls.DEEPENING]

    @classmethod
    def minors_enum(cls):
        return [
            MiniTrainingType.ACCESS_MINOR,
            MiniTrainingType.DISCIPLINARY_COMPLEMENT_MINOR,
            MiniTrainingType.OPEN_MINOR,
            MiniTrainingType.SOCIETY_MINOR
        ]

    @classmethod
    def to_postpone(cls):
        return cls.minors() + [cls.DEEPENING.name, cls.FSA_SPECIALITY.name]

    @classmethod
    def with_admission_condition(cls):
        return [
            cls.DEEPENING.name,
            cls.SOCIETY_MINOR.name,
            cls.ACCESS_MINOR.name,
            cls.OPEN_MINOR.name,
            cls.DISCIPLINARY_COMPLEMENT_MINOR.name,
            cls.FSA_SPECIALITY.name,
        ]

    @classmethod
    def with_skills_achievements(cls):
        return cls.with_admission_condition()

    @classmethod
    def mini_training_types_enum(cls) -> List[EducationGroupTypesEnum]:
        return [
            cls.DEEPENING, cls.SOCIETY_MINOR, cls.ACCESS_MINOR,
            cls.OPEN_MINOR, cls.DISCIPLINARY_COMPLEMENT_MINOR, cls.FSA_SPECIALITY, cls.OPTION, cls.MOBILITY_PARTNERSHIP
        ]


class GroupType(EducationGroupTypesEnum):
    COMMON_CORE = _("Common core")
    MINOR_LIST_CHOICE = _("Minor list choice")
    MAJOR_LIST_CHOICE = _("Major list choice")
    OPTION_LIST_CHOICE = _("Option list choice")
    FINALITY_120_LIST_CHOICE = _("Finality 120 list choice")
    FINALITY_180_LIST_CHOICE = _("Finality 180 list choice")
    MOBILITY_PARTNERSHIP_LIST_CHOICE = _("Mobility partnership list choice")
    COMPLEMENTARY_MODULE = _("Complementary module")
    SUB_GROUP = _("Sub group")

    @classmethod
    def minor_major_option_list_choice(cls):
        return [
            cls.MINOR_LIST_CHOICE.name, cls.MAJOR_LIST_CHOICE.name, cls.OPTION_LIST_CHOICE.name
        ]

    @classmethod
    def minor_major_option_list_choice_enums(cls) -> List['GroupType']:
        return [cls.MINOR_LIST_CHOICE, cls.MAJOR_LIST_CHOICE, cls.OPTION_LIST_CHOICE]

    @classmethod
    def minor_major_list_choice(cls):
        return [
            cls.MINOR_LIST_CHOICE.name, cls.MAJOR_LIST_CHOICE.name
        ]

    @classmethod
    def minor_major_list_choice_enums(cls) -> List['GroupType']:
        return [cls.MINOR_LIST_CHOICE, cls.MAJOR_LIST_CHOICE]

    @classmethod
    def ordered(cls):
        return [
            cls.COMMON_CORE.name, cls.FINALITY_120_LIST_CHOICE.name, cls.FINALITY_180_LIST_CHOICE.name,
            cls.OPTION_LIST_CHOICE.name, cls.MINOR_LIST_CHOICE.name, cls.MAJOR_LIST_CHOICE.name,
            cls.MOBILITY_PARTNERSHIP_LIST_CHOICE.name, cls.COMPLEMENTARY_MODULE.name, cls.SUB_GROUP.name
        ]


AllTypes = ChoiceEnum('AllTypes', [(t.name, t.value) for t in TrainingType] +
                      [(t.name, t.value) for t in MiniTrainingType] +
                      [(t.name, t.value) for t in GroupType])

ALL_TYPES = TrainingType.choices() + MiniTrainingType.choices() + GroupType.choices()
