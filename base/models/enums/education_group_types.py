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
# TRAINING
AGREGATION = "Agregation"
CERTIFICATE_OF_PARTICIPATION = "Certificate of participation"
CERTIFICATE_OF_SUCCESS = "Certificate of success"
CERTIFICATE_OF_HOLDING_CREDITS = "Certificate of holding credits"
BACHELOR = "Bachelor"
CERTIFICAT = "Certificat"
CAPAES = "CAPAES"
RESEARCH_CERTIFICAT = "Research certificat"
UNIVERSITY_FIRST_CYCLE_CERTIFICAT = "University first cycle certificat"
UNIVERSITY_SECOND_CYCLE_CERTIFICAT = "University second cycle certificat"
ACCESS_CONTEST = "Access contest"
LANGUAGE_CLASSE = "Language classes"
ISOLATED_CLASSE = "Isoldated classes"
PHD = "PHD"
FORMATION_PHD = "Formation PHD"
JUNIOR_YEAR = "Junior year"
PGRM_MASTER_120 = "Program master 120"
MASTER_MA_120 = "Master MA 120"
MASTER_MD_120 = "Master MD 120"
MASTER_MS_120 = "Master MS 120"
PGRM_MASTER_180_240 = "Program master 180-240"
MASTER_MA_180_240 = "Master MA 180-240"
MASTER_MD_180_240 = "Master MD 180-240"
MASTER_MS_180_240 = "Master MS 180-240"
MASTER_M1 = "Master in 60 credits"
MASTER_MC = "Master of specialist"
STAGIAIRE = "Internship"

# MINI-TRAINING
DEEPENING = "Deepening"
SOCIATY_MINOR = "Sociaty minor"
ACCESS_MINOR = "Access minor"
OPEN_MINOR = "Open minor"
DISCIPLINARY_COMPLEMENT_MINOR = "Disciplinary complement minor"
FSA_SPECIALITY = "FSA speciality"
OPTION = "Option"
MOBILITY_PARTNERSHIP = "Mobility partnership"

# GROUPS
COMMON_CORE = "Common core"
MINOR_LIST_CHOICE = "Minor list choice"
MAJOR_LIST_CHOICE = "Major list choice"
OPTION_LIST_CHOICE = "Option list choice"
FINALITY_120_LIST_CHOICE = "Finality 120 list choice"
FINALITY_180_LIST_CHOICE = "Finality 180 list choice"
MOBILITY_PARTNERSHIP_LIST_CHOICE = "Mobility partnership list choice"
COMPLEMENTARY_MODULE = "Complementary module"
SUB_GROUP = "Sub group"

MINOR = (SOCIATY_MINOR, ACCESS_MINOR, OPEN_MINOR,
         DISCIPLINARY_COMPLEMENT_MINOR)

TYPES = (
    # TRAINING
    (AGREGATION, AGREGATION),
    (CERTIFICATE_OF_PARTICIPATION, CERTIFICATE_OF_PARTICIPATION),
    (CERTIFICATE_OF_SUCCESS, CERTIFICATE_OF_SUCCESS),
    (CERTIFICATE_OF_HOLDING_CREDITS, CERTIFICATE_OF_HOLDING_CREDITS),
    (BACHELOR, BACHELOR),
    (CERTIFICAT, CERTIFICAT),
    (CAPAES, CAPAES),
    (RESEARCH_CERTIFICAT, RESEARCH_CERTIFICAT),
    (UNIVERSITY_FIRST_CYCLE_CERTIFICAT, UNIVERSITY_FIRST_CYCLE_CERTIFICAT),
    (UNIVERSITY_SECOND_CYCLE_CERTIFICAT, UNIVERSITY_SECOND_CYCLE_CERTIFICAT),
    (ACCESS_CONTEST, ACCESS_CONTEST),
    (LANGUAGE_CLASSE, LANGUAGE_CLASSE),
    (ISOLATED_CLASSE, ISOLATED_CLASSE),
    (PHD, PHD),
    (FORMATION_PHD, FORMATION_PHD),
    (JUNIOR_YEAR, JUNIOR_YEAR),
    (PGRM_MASTER_120, PGRM_MASTER_120),
    (MASTER_MA_120, MASTER_MA_120),
    (MASTER_MD_120, MASTER_MD_120),
    (MASTER_MS_120, MASTER_MS_120),
    (PGRM_MASTER_180_240, PGRM_MASTER_180_240),
    (MASTER_MA_180_240, MASTER_MA_180_240),
    (MASTER_MD_180_240, MASTER_MD_180_240),
    (MASTER_MS_180_240, MASTER_MS_180_240),
    (MASTER_M1, MASTER_M1),
    (MASTER_MC, MASTER_MC),
    (STAGIAIRE, STAGIAIRE),

    # MINI-TRAINING
    (DEEPENING, DEEPENING),
    (SOCIATY_MINOR, SOCIATY_MINOR),
    (ACCESS_MINOR, ACCESS_MINOR),
    (OPEN_MINOR, OPEN_MINOR),
    (DISCIPLINARY_COMPLEMENT_MINOR, DISCIPLINARY_COMPLEMENT_MINOR),
    (FSA_SPECIALITY, FSA_SPECIALITY),
    (OPTION, OPTION),
    (MOBILITY_PARTNERSHIP, MOBILITY_PARTNERSHIP),

    # GROUPS
    (COMMON_CORE, COMMON_CORE),
    (MINOR_LIST_CHOICE, MINOR_LIST_CHOICE),
    (MAJOR_LIST_CHOICE, MAJOR_LIST_CHOICE),
    (OPTION_LIST_CHOICE, OPTION_LIST_CHOICE),
    (FINALITY_120_LIST_CHOICE, FINALITY_120_LIST_CHOICE),
    (FINALITY_180_LIST_CHOICE, FINALITY_180_LIST_CHOICE),
    (MOBILITY_PARTNERSHIP_LIST_CHOICE, MOBILITY_PARTNERSHIP_LIST_CHOICE),
    (COMPLEMENTARY_MODULE, COMPLEMENTARY_MODULE),
    (SUB_GROUP, SUB_GROUP),
)

MINITRAINING_TO_POSTONE = [DEEPENING, SOCIATY_MINOR, ACCESS_MINOR, OPEN_MINOR, DISCIPLINARY_COMPLEMENT_MINOR]
