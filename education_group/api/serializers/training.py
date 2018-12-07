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

from base.models.academic_year import AcademicYear
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.entity import Entity
from base.models.enums import education_group_categories, organization_type


class TrainingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='education_group_api_v1:training-detail', lookup_field='uuid')
    academic_year = serializers.SlugRelatedField(slug_field='year', queryset=AcademicYear.objects.all())
    education_group_type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=EducationGroupType.objects.filter(category=education_group_categories.TRAINING),
    )
    administration_entity = serializers.SlugRelatedField(
        slug_field='most_recent_acronym',
        queryset=Entity.objects.filter(organization__type=organization_type.MAIN),
    )
    management_entity = serializers.SlugRelatedField(
        slug_field='most_recent_acronym',
        queryset=Entity.objects.filter(organization__type=organization_type.MAIN),
    )

    # Display human readable value
    education_group_type_text = serializers.CharField(source='education_group_type.get_name_display', read_only=True)
    active_text = serializers.CharField(source='get_active_display', read_only=True)

    class Meta:
        model = EducationGroupYear
        fields = (
            'url',
            'acronym',
            'education_group_type',
            'education_group_type_text',
            'partial_acronym',
            'title',
            'title_english',
            'academic_year',
            'active',
            'active_text',
            'administration_entity',
            'management_entity'
        )
