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

from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine


class AdmissionConditionsSerializer(serializers.ModelSerializer):
    free_text = serializers.SerializerMethodField(read_only=True, required=False)
    alert_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
        )

    def get_free_text(self, obj):
        return _get_appropriate_text('free', self.context.get('lang'), obj)

    def get_alert_message(self, obj):
        return _get_appropriate_text('alert_message', self.context.get('lang'), self.context.get('common'))


class BachelorAdmissionConditionsSerializer(AdmissionConditionsSerializer):
    ca_bacs_cond_generales = serializers.SerializerMethodField(method_name='get_general', read_only=True)
    ca_bacs_cond_particulieres = serializers.SerializerMethodField(method_name='get_particulieres', read_only=True)
    ca_bacs_examen_langue = serializers.SerializerMethodField(method_name='get_langue', read_only=True)
    ca_bacs_cond_speciales = serializers.SerializerMethodField(method_name='get_speciales', read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'alert_message',
            'ca_bacs_cond_generales',
            'ca_bacs_cond_particulieres',
            'ca_bacs_examen_langue',
            'ca_bacs_cond_speciales'
        )

    def get_general(self, obj):
        return _get_appropriate_text('ca_bacs_cond_generales', self.context.get('lang'), self.context.get('common'))

    def get_particulieres(self, obj):
        return _get_appropriate_text('ca_bacs_cond_particulieres', self.context.get('lang'), self.context.get('common'))

    def get_langue(self, obj):
        return _get_appropriate_text('ca_bacs_examen_langue', self.context.get('lang'), self.context.get('common'))

    def get_speciales(self, obj):
        return _get_appropriate_text('ca_bacs_cond_speciales', self.context.get('lang'), self.context.get('common'))


class SpecializedMasterAdmissionConditionsSerializer(AdmissionConditionsSerializer):
    ca_cond_generales = serializers.SerializerMethodField(method_name='get_general', read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
            'ca_cond_generales',
        )

    def get_general(self, obj):
        return _get_appropriate_text('ca_cond_generales', self.context.get('lang'), self.context.get('common'))


class AggregationAdmissionConditionsSerializer(SpecializedMasterAdmissionConditionsSerializer):
    ca_maitrise_fr = serializers.SerializerMethodField(method_name='get_maitrise', read_only=True)
    ca_allegement = serializers.SerializerMethodField(method_name='get_allegement', read_only=True)
    ca_ouv_adultes = serializers.SerializerMethodField(method_name='get_adultes', read_only=True)

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

    def get_maitrise(self, obj):
        return _get_appropriate_text('ca_maitrise_fr', self.context.get('lang'), self.context.get('common'))

    def get_allegement(self, obj):
        return _get_appropriate_text('ca_allegement', self.context.get('lang'), self.context.get('common'))

    def get_adultes(self, obj):
        return _get_appropriate_text('ca_ouv_adultes', self.context.get('lang'), self.context.get('common'))


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
        acl = obj.admissionconditionline_set
        university_types = ['bachelors_dutch', 'foreign_bachelors', 'others_bachelors_french', 'ucl_bachelors']
        second_degree_types = ['masters', 'graduates']
        return {
            'admission_enrollment_procedures': AdmissionConditionTextsSerializer(
                obj,
                context=_update_and_get_dict(self.context, 'section', 'admission_enrollment_procedures')
            ).data,
            'non_university_bachelors': AdmissionConditionTextsSerializer(
                obj,
                context=_update_and_get_dict(self.context, 'section', 'non_university_bachelors')
            ).data,
            'holders_non_university_second_degree': AdmissionConditionTextsSerializer(
                obj,
                context=_update_and_get_dict(self.context, 'section', 'holders_non_university_second_degree')
            ).data,
            'adults_taking_up_university_training': AdmissionConditionTextsSerializer(
                obj,
                context=_update_and_get_dict(self.context, 'section', 'adults_taking_up_university_training')
            ).data,
            'personalized_access': AdmissionConditionTextsSerializer(
                obj,
                context=_update_and_get_dict(self.context, 'section', 'personalized_access')
            ).data,

            'university_bachelors': {
                'text': _get_appropriate_text('university_bachelors', self.context.get('lang'), obj),
                'records': {
                    diploma_type: AdmissionConditionLineSerializer(
                        acl.all().filter(section=diploma_type),
                        many=True
                    ).data
                    for diploma_type in university_types
                }
            },
            'holders_second_university_degree': {
                'text': _get_appropriate_text('holders_second_university_degree', self.context.get('lang'), obj),
                'records': {
                    diploma_type: AdmissionConditionLineSerializer(
                        acl.all().filter(section=diploma_type),
                        many=True
                    ).data
                    for diploma_type in second_degree_types
                }
            }
        }


class AdmissionConditionTextsSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField(read_only=True)
    text_common = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'text',
            'text_common',
        )

    def get_text(self, obj):
        return _get_appropriate_text(
            self.context.get('section'),
            self.context.get('lang'),
            obj
        )

    def get_text_common(self, obj):
        return _get_appropriate_text(
            self.context.get('section'),
            self.context.get('lang'),
            self.context.get('common')
        )


class AdmissionConditionLineSerializer(serializers.ModelSerializer):
    access = serializers.CharField(source='get_access_display', read_only=True)

    class Meta:
        model = AdmissionConditionLine

        fields = (
            'access',
            'conditions',
            'diploma',
            'remarks'
        )


def _get_appropriate_text(field, language, ac):
    lang = '' if language == 'fr-be' else '_' + language
    text = getattr(ac, 'text_' + field + lang)
    return text if text else None


def _update_and_get_dict(init_dict, key, value):
    init_dict.update({key: value})
    return init_dict
