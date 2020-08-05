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
from django.conf import settings
from rest_framework import serializers

from base.models.education_group_type import EducationGroupType
from base.models.prerequisite import Prerequisite
from education_group.api.serializers.education_group_title import EducationGroupTitleSerializer
from education_group.api.serializers.training import TrainingHyperlinkedIdentityField
from education_group.api.serializers.utils import TrainingHyperlinkedRelatedField
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository


class EducationGroupRootsListSerializer(EducationGroupTitleSerializer, serializers.HyperlinkedModelSerializer):
    url = TrainingHyperlinkedIdentityField(read_only=True)
    acronym = serializers.CharField(source='offer.acronym', read_only=True)
    academic_year = serializers.IntegerField(source='offer.academic_year.year')
    education_group_type = serializers.SlugRelatedField(
        source='offer.education_group_type',
        slug_field='name',
        queryset=EducationGroupType.objects.all(),
    )
    code = serializers.CharField(source='root_group.partial_acronym', read_only=True)
    decree_category = serializers.CharField(source='offer.decree_category', read_only=True)
    duration_unit = serializers.CharField(source='offer.duration_unit', read_only=True)
    credits = serializers.IntegerField(source='root_group.credits', read_only=True)
    duration = serializers.IntegerField(source='offer.duration', read_only=True)

    # Display human readable value
    education_group_type_text = serializers.CharField(source='offer.education_group_type.get_name_display',
                                                      read_only=True)
    decree_category_text = serializers.CharField(source='offer.get_decree_category_display', read_only=True)
    duration_unit_text = serializers.CharField(source='offer.get_duration_unit_display', read_only=True)
    learning_unit_credits = serializers.SerializerMethodField(read_only=True)

    class Meta(EducationGroupTitleSerializer.Meta):
        fields = EducationGroupTitleSerializer.Meta.fields + (
            'url',
            'acronym',
            'code',
            'credits',
            'decree_category',
            'decree_category_text',
            'duration',
            'duration_unit',
            'duration_unit_text',
            'education_group_type',
            'education_group_type_text',
            'academic_year',
            'learning_unit_credits',
        )

    def get_learning_unit_credits(self, obj):
        learning_unit_year = self.context['learning_unit_year']
        identity = ProgramTreeVersionIdentity(
            offer_acronym=obj.offer.acronym,
            year=obj.offer.academic_year.year,
            version_name=obj.version_name,
            is_transition=obj.is_transition
        )

        tree = ProgramTreeVersionRepository().get(entity_id=identity).get_tree()
        node = tree.get_node_by_code_and_year(
            code=learning_unit_year.acronym, year=learning_unit_year.academic_year.year
        )
        link = tree.get_links_using_node(node)[0]

        return link.relative_credits or (learning_unit_year and learning_unit_year.credits)


# TODO :: OSIS-4735
class LearningUnitYearPrerequisitesListSerializer(serializers.ModelSerializer):
    url = TrainingHyperlinkedRelatedField(
        source='education_group_version',
        lookup_field='acronym', read_only=True
    )

    acronym = serializers.CharField(source='education_group_version.offer.acronym')
    code = serializers.CharField(
        source='education_group_version.root_group.partial_acronym')  # TODO: Get from GroupYear
    academic_year = serializers.IntegerField(source='education_group_version.offer.academic_year.year')
    education_group_type = serializers.SlugRelatedField(
        source='education_group_version.offer.education_group_type',
        slug_field='name',
        queryset=EducationGroupType.objects.all(),
    )
    education_group_type_text = serializers.CharField(
        source='education_group_version.offer.education_group_type.get_name_display',
        read_only=True,
    )
    prerequisites = serializers.CharField(source='prerequisite_string')
    title = serializers.SerializerMethodField()

    class Meta:
        model = Prerequisite
        fields = (
            'url',
            'title',
            'acronym',
            'code',
            'academic_year',
            'education_group_type',
            'education_group_type_text',
            'prerequisites'
        )

    def get_title(self, prerequisite):
        language = self.context['language']
        return getattr(
            prerequisite.education_group_version.root_group,
            'title_' + ('en' if language not in settings.LANGUAGE_CODE_FR else 'fr')
        )
