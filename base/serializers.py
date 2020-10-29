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

from base.models.entity import Entity
from base.models.entity_version import EntityVersion
from base.models.entity_version_address import EntityVersionAddress


class EntityVersionAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityVersionAddress
        fields = ('location', 'postal_code', 'city', 'country')


class EntityVersionSerializer(serializers.ModelSerializer):
    entityversionaddress_set = EntityVersionAddressSerializer(many=True)

    class Meta:
        model = EntityVersion
        fields = ('acronym', 'title', 'entity_type', 'parent', 'start_date', 'end_date', 'external_id',
                  'entityversionaddress_set')

    def create(self, validated_data):
        addresses_data = validated_data.pop('entityversionaddress_set')

        entity_version = EntityVersion.objects.create(**validated_data)
        for address_data in addresses_data:
            EntityVersionAddress.objects.create(entity_version=entity_version, **address_data)
        return entity_version


class EntitySerializer(serializers.ModelSerializer):
    entityversion_set = EntityVersionSerializer(many=True)

    class Meta:
        model = Entity
        fields = ('id', 'organization', 'external_id', 'website', 'entityversion_set',
                  'location', 'postal_code', 'city', 'country')

    def create(self, validated_data):
        versions_data = validated_data.pop('entityversion_set')

        entity = Entity.objects.create(**validated_data)

        for version_data in versions_data:
            EntityVersion.objects.create(entity=entity, **version_data)

        return entity
