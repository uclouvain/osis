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

from base.models.entity_version import EntityVersion
from base.models.person import Person


class PersonDetailSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = Person
        fields = (
            'first_name',
            'last_name',
            'email',
            'gender',
            'uuid'
        )


class PersonRolesSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = (
            'global_id',
            'roles'
        )

    def get_roles(self, obj):
        entities_acronym = set()
        for person_entity in obj.personentity_set.all():
            if not person_entity.with_child:
                acronyms = {person_entity.entity.most_recent_acronym}
            else:
                acronyms = set(row['acronym'] for row in EntityVersion.objects.get_tree(person_entity.entity))
            entities_acronym |= acronyms

        return entities_acronym
