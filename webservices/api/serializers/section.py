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

from rest_framework import serializers

from webservices.api.serializers.achievement import AchievementsSerializer
from webservices.api.serializers.admission_condition import AdmissionConditionsSerializer, \
    BachelorAdmissionConditionsSerializer, SpecializedMasterAdmissionConditionsSerializer, \
    AggregationAdmissionConditionsSerializer, MasterAdmissionConditionsSerializer


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
        language = self.context.get('lang')
        admission_condition_common = egy.admissioncondition.common_admission_condition
        context = {
            'lang': language,
            'common': admission_condition_common,
        }
        if egy.is_bachelor:
            return BachelorAdmissionConditionsSerializer(egy.admissioncondition, lang=language).data
        elif egy.is_specialized_master:
            return SpecializedMasterAdmissionConditionsSerializer(egy.admissioncondition, lang=language).data
        elif egy.is_aggregation:
            return AggregationAdmissionConditionsSerializer(egy.admissioncondition, lang=language).data
        elif any([egy.is_master120, egy.is_master60, egy.is_master180]):
            return MasterAdmissionConditionsSerializer(egy.admissioncondition, lang=language, context=context).data
        else:
            return AdmissionConditionsSerializer(egy.admissioncondition, lang=language).data
