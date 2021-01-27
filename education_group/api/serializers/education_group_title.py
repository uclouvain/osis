##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from rest_framework import serializers

from program_management.models.education_group_version import EducationGroupVersion


class EducationGroupTitleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = EducationGroupVersion
        fields = (
            'title',
        )

    def get_title(self, version):
        return _get_offer_title_from_lang(version, self.context.get('language', settings.LANGUAGE_CODE_FR))


class EducationGroupTitleAllLanguagesSerializer(EducationGroupTitleSerializer):
    title_en = serializers.SerializerMethodField()

    class Meta(EducationGroupTitleSerializer.Meta):
        fields = EducationGroupTitleSerializer.Meta.fields + (
            'title_en',
        )

    @staticmethod
    def get_title_en(version):
        return _get_offer_title_from_lang(version, settings.LANGUAGE_CODE_EN)


def _get_offer_title_from_lang(version, lang: str):
    version_field_name = 'title' + ('_en' if lang == settings.LANGUAGE_CODE_EN else '_fr')
    title = getattr(version.offer, 'title' + ('_english' if lang == settings.LANGUAGE_CODE_EN else ''))
    version_title = getattr(version, version_field_name)
    title_suffix = ' [{}]'.format(version_title) if version_title else ''
    return title + title_suffix if title else None
