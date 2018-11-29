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
from django.conf import settings
from django.db.models import Prefetch

from base.models.education_group_achievement import EducationGroupAchievement
from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement
from cms.enums import entity_name
from cms.models.translated_text import TranslatedText

SKILLS_AND_ACHIEVEMENTS_KEY = 'comp_acquis'
SKILLS_AND_ACHIEVEMENTS_AA_DATA = 'achievements'
SKILLS_AND_ACHIEVEMENTS_CMS_DATA = ('skills_and_achievements_introduction', 'skills_and_achievements_additional_text', )


def get_achievements(education_group_year, language_code):
    if language_code in [settings.LANGUAGE_CODE_FR, settings.LANGUAGE_CODE_EN]:
        return EducationGroupAchievement.objects.filter(
            education_group_year=education_group_year
        ).prefetch_related(
            Prefetch(
                'educationgroupdetailedachievement_set',
                queryset=EducationGroupDetailedAchievement.objects.all().annotate_text(language_code),
                to_attr='detailed_achievements',
            ),
        ).annotate_text(language_code)
    raise AttributeError('Language code not supported {}'.format(language_code))


def get_intro_extra_content_achievements(education_group_year, language_code):
    qs = TranslatedText.objects.filter(
        entity=entity_name.OFFER_YEAR,
        reference=education_group_year.id,
        language=language_code,
        text_label__label__in=SKILLS_AND_ACHIEVEMENTS_CMS_DATA
    ).select_related('text_label')
    return {cms_data.text_label.label: cms_data.text for cms_data in qs}
