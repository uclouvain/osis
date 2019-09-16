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
from django.db.models import Value, CharField
from rest_framework import serializers

from base.business.education_groups.general_information_sections import SECTIONS_PER_OFFER_TYPE, \
    SKILLS_AND_ACHIEVEMENTS_KEY
from base.models.education_group_year import EducationGroupYear
from cms.enums.entity_name import OFFER_YEAR
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from education_group.api.serializers.section import SectionSerializer, AchievementSectionSerializer
from webservices.business import EVALUATION_KEY, get_evaluation_text


class GeneralInformationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(read_only=True)
    year = serializers.IntegerField(source='academic_year.year', read_only=True)
    sections = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EducationGroupYear

        fields = (
            'language',
            'acronym',
            'title',
            'year',
            'sections'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.language = kwargs['context']['language']

    def get_sections(self, obj):
        sections = []
        achievements = None
        language = 'fr-be' if self.instance.language == 'fr' else self.instance.language
        pertinent_sections = SECTIONS_PER_OFFER_TYPE[obj.education_group_type.name]
        common_egy = EducationGroupYear.objects.get_common(
            academic_year=obj.academic_year
        )

        for common_section in pertinent_sections['common']:
            common_translated_text, _ = self._get_translated_text(common_egy, common_section, language)
            sections.append(common_translated_text)

        for specific_section in pertinent_sections['specific']:
            if specific_section == SKILLS_AND_ACHIEVEMENTS_KEY:
                achievements = AchievementSectionSerializer(
                    {'id': specific_section},
                    context={'egy': obj, 'lang': language}
                )
            elif specific_section != EVALUATION_KEY:
                translated_text, translated_text_label = self._get_translated_text(obj, specific_section, language)

                sections.append(translated_text if translated_text else {
                    'label': specific_section,
                    'translated_label': translated_text_label.label
                })

        return SectionSerializer(sections, many=True).data + [achievements.data] if achievements else []

    def _get_translated_text(self, egy, section, language):
        translated_text_label = TranslatedTextLabel.objects.filter(
            text_label__label=section,
            language=language,
        ).first()
        translated_text = TranslatedText.objects.filter(
            text_label__label=section,
            language=language,
            entity=OFFER_YEAR,
            reference=egy.id
        ).annotate(
                label=Value(section, output_field=CharField()),
                translated_label=Value(translated_text_label.label, output_field=CharField())
        )
        if section == EVALUATION_KEY:
            translated_text = self._get_evaluation_text(language, translated_text)
        else:
            translated_text = translated_text.values(
                'label', 'translated_label', 'text'
            ).first()

        return translated_text, translated_text_label

    def _get_evaluation_text(self, language, translated_text):
        try:
            _, text = get_evaluation_text(self.instance, language)
        except TranslatedText.DoesNotExist:
            text = None
        translated_text = translated_text.annotate(
            free_text=Value(text, output_field=CharField())
        ).values(
            'label', 'translated_label', 'text', 'free_text'
        ).first()
        return translated_text
