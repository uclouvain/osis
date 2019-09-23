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

from backoffice.settings.rest_framework import common_serializers


class LearningUnitSummarySpecificationSerializer(serializers.Serializer):
    bibliography = common_serializers.TranslatedSerializer()
    resume = common_serializers.TranslatedSerializer()
    evaluation_methods = common_serializers.TranslatedSerializer()
    other_informations = common_serializers.TranslatedSerializer()
    online_resources = common_serializers.TranslatedSerializer()
    teaching_methods = common_serializers.TranslatedSerializer()
    themes_discussed = common_serializers.TranslatedSerializer()
    prerequisite = common_serializers.TranslatedSerializer()
    mobility = common_serializers.TranslatedSerializer()


class LearningUnitSummarySpecificationSpecificLanguageSerializer(serializers.Serializer):
    bibliography = serializers.CharField()
    resume = serializers.CharField()
    evaluation_methods = serializers.CharField()
    other_informations = serializers.CharField()
    online_resources = serializers.CharField()
    teaching_methods = serializers.CharField()
    themes_discussed = serializers.CharField()
    prerequisite = serializers.CharField()
    mobility = serializers.CharField()
