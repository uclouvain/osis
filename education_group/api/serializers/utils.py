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
from rest_framework.reverse import reverse

from base.models.enums.education_group_categories import Categories


class EducationGroupYearHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    default_view = 'education_group_api_v1:training_read'

    lookup_field = None

    def __init__(self, lookup_field=None, **kwargs):
        self.lookup_field = lookup_field or ''
        super().__init__(view_name=self.default_view, **kwargs)

    @staticmethod
    def _get_view_name(category):
        return {
            Categories.TRAINING.name: 'education_group_api_v1:training_read',
            Categories.MINI_TRAINING.name: 'education_group_api_v1:mini_training_read',
            Categories.GROUP.name: 'education_group_api_v1:group_read',
        }[category]

    @staticmethod
    def _get_view_kwargs(education_group_year):
        acronym_key = {
            Categories.TRAINING.name: 'acronym',
            Categories.MINI_TRAINING.name: 'partial_acronym',
            Categories.GROUP.name: 'partial_acronym',
        }[education_group_year.education_group_type.category]
        return {
            acronym_key: getattr(education_group_year, acronym_key, education_group_year),
            'year': education_group_year.academic_year.year
        }

    def get_url(self, obj, view_name, request, format):
        education_group_year = obj
        for attr in self.lookup_field.split('__'):
            education_group_year = getattr(education_group_year, attr, education_group_year)

        category = education_group_year.education_group_type.category

        return reverse(
            self._get_view_name(category),
            kwargs=self._get_view_kwargs(education_group_year),
            request=request,
            format=format
        )


# FIXME :: deprecated : use EducationGroupYearHyperlinkedIdentityField instead
class TrainingGetUrlMixin:
    def __init__(self, **kwargs):
        super().__init__(view_name='education_group_api_v1:training_read', **kwargs)

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'acronym': obj.acronym,
            'year': obj.academic_year.year
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class TrainingHyperlinkedIdentityField(TrainingGetUrlMixin, serializers.HyperlinkedIdentityField):
    pass


class TrainingHyperlinkedRelatedField(TrainingGetUrlMixin, serializers.HyperlinkedRelatedField):
    pass


# FIXME :: deprecated : use EducationGroupYearHyperlinkedIdentityField instead
class MiniTrainingGetUrlMixin:
    def __init__(self, **kwargs):
        super().__init__(view_name='education_group_api_v1:mini_training_read', **kwargs)

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'partial_acronym': obj.partial_acronym,
            'year': obj.academic_year.year
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class MiniTrainingHyperlinkedIdentityField(MiniTrainingGetUrlMixin, serializers.HyperlinkedIdentityField):
    pass


# FIXME :: deprecated : use EducationGroupYearHyperlinkedIdentityField instead
class GroupGetUrlMixin:
    def __init__(self, **kwargs):
        super().__init__(view_name='education_group_api_v1:group_read', **kwargs)

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'partial_acronym': obj.partial_acronym,
            'year': obj.academic_year.year
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class GroupHyperlinkedIdentityField(GroupGetUrlMixin, serializers.HyperlinkedIdentityField):
    pass
