##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.learning_unit_year import LearningUnitYear
from learning_unit.api.serializers.campus import LearningUnitCampusSerializer
from learning_unit.api.serializers.component import LearningUnitComponentSerializer


class LearningUnitDetailedSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='learning_unit_api_v1:learningunits_read',
        lookup_field='uuid',
        read_only=True
    )

    periodicity_text = serializers.CharField(source='get_periodicity_display', read_only=True)
    quadrimester_text = serializers.CharField(source='get_quadrimester_display', read_only=True)

    requirement_entity = serializers.CharField(
        source='learning_container_year.requirement_entity_version.acronym',
        read_only=True
    )
    language = serializers.CharField(source='language.code', read_only=True)
    team = serializers.BooleanField(source='learning_container_year.team', read_only=True)

    campus = LearningUnitCampusSerializer(read_only=True)
    components = LearningUnitComponentSerializer(many=True, source='learningcomponentyear_set', read_only=True)

    parent = serializers.HyperlinkedRelatedField(
        view_name='learning_unit_api_v1:learningunits_read',
        lookup_field='uuid',
        read_only=True
    )
    partims = serializers.HyperlinkedRelatedField(
        view_name='learning_unit_api_v1:learningunits_read',
        lookup_field='uuid',
        many=True,
        source='get_partims_related',
        read_only=True
    )

    class Meta:
        model = LearningUnitYear
        fields = (
            'url',
            'acronym',
            'credits',
            'requirement_entity',
            'status',
            'quadrimester',
            'quadrimester_text',
            'periodicity',
            'periodicity_text',
            'campus',
            'team',
            'language',
            'components',
            'parent',
            'partims'
        )
