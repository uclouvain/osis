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

Section = namedtuple('Section', 'title labels')

SECTION_LIST = [
    Section(title=_('Welcome'),
            labels=[
                ('welcome_introduction', 'specific'),
                ('welcome_profil', 'specific'),
                ('welcome_job', 'specific'),
                ('welcome_programme', 'specific'),
                ('welcome_parcours', 'specific'),
            ]),
    Section(title=_('Teaching profile'),
            labels=[
                ('structure', 'specific')
            ]),
    Section(title=_('Detailed programme'),
            labels=[
                ('mineures', 'specific'),
                ('majeures', 'specific'),
                ('programme_detaille', 'specific'),
                ('finalites', 'specific'),
                ('options', 'specific'),
                ('finalites_didactiques', 'common'),
                ('caap', 'common,specific'),
                ('agregation', 'common'),
                ('prerequis', 'common'),
            ]),
    Section(title=_('Admission'),
            labels=[
                ('acces_professions', 'specific'),
                ('bacheliers_concernes', 'specific'),
                ('module_complementaire', 'common,specific')
            ]),
    Section(title=_('Benefits and organization'),
            labels=[
                ('pedagogie', 'specific'),
                ('evaluation', 'common,specific'),
                ('mobilite', 'specific'),
                ('formations_accessibles', 'specific'),
                ('certificats', 'specific'),
                ('infos_pratiques', 'specific'),
            ]),
]

SECTION_INTRO = [
    Section(title=_('Welcome'),
            labels=[
                ('intro', 'specific'),
            ])
]

COMMON_GENERAL_INFO_SECTIONS = [
    'agregation',
    'caap',
    'prerequis',
    'finalites_didactiques',
    'module_complementaire',
    'evaluation'
]
