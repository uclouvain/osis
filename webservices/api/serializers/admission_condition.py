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

from base.models.admission_condition import AdmissionCondition
from webservices.api.serializers.admission_condition_line import AdmissionConditionTextsSerializer, \
    AdmissionConditionLineSerializer
from webservices.api.serializers.utils import DynamicLanguageFieldsModelSerializer


class AdmissionConditionsSerializer(DynamicLanguageFieldsModelSerializer):
    free_text = serializers.CharField(read_only=True, required=False)
    alert_message = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(AdmissionConditionsSerializer, self).__init__(*args, **kwargs)
        if not self.instance.common_admission_condition:
            self.fields.pop('alert_message')

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
        )


class BachelorAdmissionConditionsSerializer(AdmissionConditionsSerializer):
    ca_bacs_cond_generales = serializers.CharField(read_only=True)
    ca_bacs_cond_particulieres = serializers.CharField(read_only=True)
    ca_bacs_examen_langue = serializers.CharField(read_only=True)
    ca_bacs_cond_speciales = serializers.CharField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'alert_message',
            'ca_bacs_cond_generales',
            'ca_bacs_cond_particulieres',
            'ca_bacs_examen_langue',
            'ca_bacs_cond_speciales'
        )


class SpecializedMasterAdmissionConditionsSerializer(AdmissionConditionsSerializer):
    ca_cond_generales = serializers.CharField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
            'ca_cond_generales',
        )


class AggregationAdmissionConditionsSerializer(SpecializedMasterAdmissionConditionsSerializer):
    ca_maitrise_fr = serializers.CharField(read_only=True)
    ca_allegement = serializers.CharField(read_only=True)
    ca_ouv_adultes = serializers.CharField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
            'ca_cond_generales',
            'ca_maitrise_fr',
            'ca_allegement',
            'ca_ouv_adultes'
        )


class MasterAdmissionConditionsSerializer(AdmissionConditionsSerializer):
    sections = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
            'sections',
        )

    def get_sections(self, obj):
        university_types = ['bachelors_dutch', 'foreign_bachelors', 'others_bachelors_french', 'ucl_bachelors']
        second_degree_types = ['masters', 'graduates']
        acl_fields = [
            ('university_bachelors', university_types),
            ('holders_second_university_degree', second_degree_types)
        ]
        ac_fields = [
            'admission_enrollment_procedures',
            'non_university_bachelors',
            'holders_non_university_second_degree',
            'adults_taking_up_university_training',
            'personalized_access',
        ]
        sections = {
            field: AdmissionConditionTextsSerializer(
                obj,
                lang=self.context.get('lang'),
                context=_update_and_get_dict(self.context, 'section', field)
            ).data
            for field in ac_fields
        }
        sections_line = {
            field: {
                'text': _get_appropriate_text(field, self.context.get('lang'), obj),
                'records': {
                    diploma_type: AdmissionConditionLineSerializer(
                        obj.admissionconditionline_set.filter(section=diploma_type),
                        many=True,
                        lang=self.context.get('lang'),
                        context=self.context
                    ).data
                    for diploma_type in diploma_types
                }
            } for field, diploma_types in acl_fields
        }
        sections.update(sections_line)
        return sections


def _get_appropriate_text(field, language, ac):
    lang = '' if language == 'fr-be' else '_' + language
    text = getattr(ac, 'text_' + field + lang)
    return text if text else None


def _update_and_get_dict(init_dict, key, value):
    init_dict.update({key: value})
    return init_dict
