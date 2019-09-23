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
from collections import OrderedDict

from django.db.models.functions import Lower
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from base.models.learning_achievement import LearningAchievement
from base.models.learning_unit_year import LearningUnitYear
from learning_unit.api.serializers.learning_achievement import LearningAchievementListSerializer


class LearningAchievementList(generics.GenericAPIView):
    """
        Return all achievement in order according of the learning unit specified.
    """
    name = 'learningunitachievements_read'
    serializer_class = LearningAchievementListSerializer
    filter_backends = []
    paginator = None

    def get(self, request, *args, **kwargs):
        learning_unit_year = get_object_or_404(
            LearningUnitYear.objects.all(),
            acronym=self.kwargs.pop('acronym').upper(),
            academic_year__year=self.kwargs.pop('year')
        )
        qs = LearningAchievement.objects.filter(learning_unit_year=learning_unit_year).order_by('order')\
                                .annotate(iso_code=Lower('language__code')).values('code_name', 'text', 'iso_code')

        learning_achievements_grouped = OrderedDict()
        for learning_achievement in qs:
            code_name = learning_achievement['code_name']
            learning_achievements_grouped.setdefault(code_name, {'fr': '', 'en': '', 'code_name': code_name})
            learning_achievements_grouped[code_name][learning_achievement['iso_code']] = \
                learning_achievement['text']

        serializer = self.get_serializer(learning_achievements_grouped.values(), many=True)
        return Response(serializer.data)
