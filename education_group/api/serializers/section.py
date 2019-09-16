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
import re

from rest_framework import serializers

from education_group.api.serializers.achievement import AchievementsSerializer
from education_group.api.serializers.admission_condition import AdmissionConditionsSerializer

ACRONYM_PATTERN = re.compile(r'(?P<prefix>[a-z]+)(?P<cycle>[0-9]{1,3})(?P<suffix>[a-z]+)(?P<year>[0-9]?)')


class AcronymError(Exception):
    pass


class SectionSerializer(serializers.Serializer):
    id = serializers.CharField(source='label', read_only=True)
    label = serializers.CharField(source='translated_label', read_only=True)
    content = serializers.CharField(source='text', read_only=True, allow_null=True)
    free_text = serializers.CharField(read_only=True, required=False)

    class Meta:
        fields = (
            'id',
            'label',
            'content',
            'free_text'
        )


class AchievementSectionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    label = serializers.CharField(source='id', read_only=True)
    content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id',
            'label',
            'content',
        )

    def get_content(self, obj):
        egy = self.context.get('egy')
        return AchievementsSerializer(egy, context=self.context).data


class AdmissionConditionSectionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    label = serializers.CharField(source='id', read_only=True)
    content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id',
            'label',
            'content',
        )

    def get_content(self, obj):
        egy = self.context.get('egy')
        acronym_match = re.match(ACRONYM_PATTERN, egy.acronym.lower())
        if not acronym_match:
            raise AcronymError("The acronym does not match the pattern")

        full_suffix = '{cycle}{suffix}{year}'.format(**acronym_match.groupdict())
        return AdmissionConditionsSerializer(
            egy.admissioncondition,
            context={
                'lang': self.context.get('lang'),
                'full_suffix': full_suffix,
                'egy': egy
            }
        ).data
        # ACRONYM_PATTERN = re.compile(r'(?P<prefix>[a-z]+)(?P<cycle>[0-9]{1,3})(?P<suffix>[a-z]+)(?P<year>[0-9]?)')
        # acronym_match = re.match(ACRONYM_PATTERN, egy.acronym.lower())
        # if not acronym_match:
        #     raise AcronymError("The acronym does not match the pattern")
        #
        # acronym_suffix = acronym_match.group('suffix').lower()
        #
        # full_suffix = '{cycle}{suffix}{year}'.format(**acronym_match.groupdict())
        #
        # is_bachelor = acronym_suffix == 'ba'
        #
        # if is_bachelor:
        #     # special case, if it's a bachelor, just return the text for the bachelor
        #     return response_for_bachelor(self.context)
        #
        # common_acronym = 'common-{}'.format(full_suffix)
        # if common_acronym == 'common-2m1':
        #     common_acronym = 'common-2m'
        #     full_suffix = '2m'
        # admission_condition, created = AdmissionCondition.objects.get_or_create(
        #     education_group_year=egy
        # )
        # admission_condition_common = None
        #
        # if full_suffix.upper() in COMMON_OFFER:
        #     common_education_group_year = EducationGroupYear.objects.get(
        #         acronym=common_acronym,
        #         academic_year=egy.academic_year
        #     )
        #     admission_condition_common = common_education_group_year.admissioncondition
        # self.context.suffix_language = self.context['lang']
        # print(self.context)
        # result = {
        #     'id': 'conditions_admission',
        #     "label": "conditions_admission",
        #     "content": build_content_response(self.context, admission_condition, admission_condition_common, full_suffix)
        # }
        # return result
