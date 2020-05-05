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

from typing import List

from base.models.learning_achievement import LearningAchievement
from learning_unit.ddd.domain.achievement import Achievement

from django.db.models import F


def load_achievements(acronym: str, year: int) -> List['Achievement']:
    qs = LearningAchievement.objects.filter(
        learning_unit_year__acronym=acronym,
        learning_unit_year__academic_year__year=year)\
        .annotate(language_code=F('language__code'))\
        .values('code_name', 'text', 'language_code', 'order')\
        .order_by('order', 'language_code')

    return _build_achievements(qs)


def _build_achievements(qs):
    # TODO : Je n'arrive pas à faire autrement que comme ceci
    current_order = None
    achievements = []
    code_name = None
    text_fr = None
    text_en = None
    for achievement_rec in qs:
        if current_order is None:
            current_order = achievement_rec['order']
        if achievement_rec['order'] != current_order:
            achievements.append(Achievement(code_name=code_name, text_fr=text_fr, text_en=text_en))
            current_order = achievement_rec['order']

        code_name = achievement_rec['code_name']
        if achievement_rec['language_code'] == 'EN':
            text_en = achievement_rec['text']
        if achievement_rec['language_code'] == 'FR':
            text_fr = achievement_rec['text']
    achievements.append(Achievement(code_name=code_name, text_fr=text_fr, text_en=text_en))
    return achievements
