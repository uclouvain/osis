
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
from learning_unit.api.serializers.campus import CampusSerializer


class LearningUnitYearSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='learning_unit_api_v1:learningunits_read',
        lookup_field='uuid'
    )
    requirement_entity = serializers.CharField(source='requirement_entity_version.acronym', read_only=True)
    language = serializers.CharField(source='language.code', read_only=True)
    team = serializers.BooleanField(source='learning_container_year.team', read_only=True)
    campus = CampusSerializer()

    class Meta:
        model = LearningUnitYear
        fields = (
            'url',
            'acronym',
            'credits',
            'requirement_entity',
            'status',
            'quadrimester',
            'periodicity',
            'campus',
            'team',
            'language'
        )

    def get_campus(self, obj):
        return {
            'name': obj.campus.name,
            'organization': obj.campus.organization.name
        }
