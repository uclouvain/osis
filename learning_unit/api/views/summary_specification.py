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
from django.db.models import Case, When, CharField, F, Value
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from backoffice.settings.base import LANGUAGE_CODE_FR, LANGUAGE_CODE_EN
from base.business.learning_unit import CMS_LABEL_PEDAGOGY, CMS_LABEL_SPECIFICATIONS
from base.models.learning_unit_year import LearningUnitYear
from cms.models.translated_text import TranslatedText
from learning_unit.api.serializers.summary_specification import LearningUnitSummarySpecificationSerializer


class LearningUnitSummarySpecification(generics.GenericAPIView):
    """
        Return all summary and specification information of the learning unit specified
    """
    name = 'learningunitsummaryspecification_read'
    serializer_class = LearningUnitSummarySpecificationSerializer
    filter_backends = []
    paginator = None

    def get(self, request, *args, **kwargs):
        learning_unit_year = get_object_or_404(LearningUnitYear.objects.all(), uuid=kwargs['uuid'])
        qs = TranslatedText.objects.filter(
            reference=learning_unit_year.pk,
            text_label__label__in=CMS_LABEL_PEDAGOGY + CMS_LABEL_SPECIFICATIONS
        ).annotate(
            iso_code=Case(
                When(language=LANGUAGE_CODE_FR, then=Value('fr')),
                When(language=LANGUAGE_CODE_EN, then=Value('en')),
                default=None,
                output_field=CharField(),
            ),
            label=F('text_label__label')
        ).exclude(iso_code__isnull=True).values('label', 'iso_code', 'text')

        summary_specification_grouped = {}
        for translated_text in qs:
            key = translated_text['label']
            summary_specification_grouped.setdefault(key, {'fr': '', 'en': ''})
            summary_specification_grouped[key][translated_text['iso_code']] = translated_text['text']

        serializer = self.get_serializer(summary_specification_grouped)
        return Response(serializer.data)
