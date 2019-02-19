##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from collections import namedtuple

from django.utils.translation import ugettext_lazy as _

# This all text_label which are related to "general information" for education group year
# The key MUST be in french because it depend on Webservice (filtering)
from base.models.enums.education_group_types import TrainingType

PEDAGOGY = 'pedagogie'
MOBILITY = 'mobilite'
FURTHER_TRAININGS = 'formations_accessibles'
CERTIFICATES = 'certificats'
COMPLEMENTARY_MODULE = 'module_complementaire'
EVALUATION = 'evaluation'
STRUCTURE = 'structure'
DETAILED_PROGRAM = 'programme_detaille'
WELCOME_INTRODUCTION = 'welcome_introduction'
WELCOME_JOB = 'welcome_job'
WELCOME_PROFIL = 'welcome_profil'
WELCOME_PROGRAM = 'welcome_programme'
WELCOME_PATH = 'welcome_parcours'
CAAP = 'caap'
ACCESS_TO_PROFESSIONS = 'acces_professions'
BACHELOR_CONCERNED = 'bacheliers_concernes'
PRACTICAL_INFO = 'infos_pratiques'
MINORS = 'mineures'
MAJORS = 'majeures'
PURPOSES = 'finalites'
COMMON_DIDACTIC_PURPOSES = 'finalites_didactiques-commun'
AGREGATION = 'agregation'
PREREQUISITE = 'prerequis'
OPTIONS = 'options'
INTRODUCTION = 'intro'
CONTACTS = 'contacts'

Section = namedtuple('Section', 'title labels')

SECTION_LIST = [
    Section(title=_('Welcome'),
            labels=[
                (WELCOME_INTRODUCTION, 'specific'),
                (WELCOME_PROFIL, 'specific'),
                (WELCOME_JOB, 'specific'),
                (WELCOME_PROGRAM, 'specific'),
                (WELCOME_PATH, 'specific'),
            ]),
    Section(title=_('Teaching profile'),
            labels=[
                (STRUCTURE, 'specific')
            ]),
    Section(title=_('Detailed program'),
            labels=[
                (MINORS, 'specific'),
                (MAJORS, 'specific'),
                (DETAILED_PROGRAM, 'specific'),
                (PURPOSES, 'specific'),
                (OPTIONS, 'specific'),
                (COMMON_DIDACTIC_PURPOSES, 'common'),
                (CAAP, 'common,specific'),
                (AGREGATION, 'common'),
                (PREREQUISITE, 'common,specific'),
            ]),
    Section(title=_('Admission'),
            labels=[
                (ACCESS_TO_PROFESSIONS, 'specific'),
                (BACHELOR_CONCERNED, 'specific'),
                (COMPLEMENTARY_MODULE, 'common,specific')
            ]),
    Section(title=_('Benefits and organization'),
            labels=[
                (PEDAGOGY, 'specific'),
                (EVALUATION, 'common,specific'),
                (MOBILITY, 'specific'),
                (FURTHER_TRAININGS, 'specific'),
                (CERTIFICATES, 'specific'),
            ]),
    Section(title=_('In practice'),
            labels=[
                (PRACTICAL_INFO, 'specific'),
                (CONTACTS, 'specific'),
            ]),
]

SECTION_INTRO = [
    Section(title=_('Welcome'),
            labels=[
                (INTRODUCTION, 'specific'),
            ])
]

SECTION_DIDACTIC = [
    Section(title=_('Detailed program'),
            labels=[
                (COMMON_DIDACTIC_PURPOSES, 'common'),
            ])
]

COMMON_GENERAL_INFO_SECTIONS = [
    AGREGATION,
    CAAP,
    PREREQUISITE,
    COMMON_DIDACTIC_PURPOSES,
    COMPLEMENTARY_MODULE,
    EVALUATION
]

# Common type which have admission conditions sections + relevant sections
COMMON_TYPE_ADMISSION_CONDITIONS = {
    TrainingType.BACHELOR.name:
        ('alert_message', 'ca_bacs_cond_generales', 'ca_bacs_cond_particulieres',
         'ca_bacs_examen_langue', 'ca_bacs_cond_speciales', ),
    TrainingType.AGGREGATION.name:
        ('alert_message', 'ca_bacs_cond_generales', 'ca_maitrise_fr',
         'ca_allegement', 'ca_ouv_adultes', ),
    TrainingType.PGRM_MASTER_120.name:
        ('alert_message', 'non_university_bachelors', 'adults_taking_up_university_training',
         'personalized_access', 'admission_enrollment_procedures', ),
    TrainingType.MASTER_MC.name: ('alert_message', 'ca_cond_generales', )
}

MIN_YEAR_TO_DISPLAY_GENERAL_INFO_AND_ADMISSION_CONDITION = 2017
