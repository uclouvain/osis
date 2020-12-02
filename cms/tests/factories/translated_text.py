##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import factory.fuzzy
from django.conf import settings

from .text_label import TextLabelFactory
from ...enums import entity_name


class TranslatedTextFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "cms.TranslatedText"

    language = settings.LANGUAGE_CODE_FR  # French default
    text_label = factory.SubFactory(TextLabelFactory)
    entity = factory.fuzzy.FuzzyText(prefix="Entity ", length=15)
    reference = factory.fuzzy.FuzzyInteger(1, 10)
    text = None


class TranslatedTextRandomFactory(TranslatedTextFactory):
    text = factory.Faker('paragraph', nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)


class EnglishTranslatedTextRandomFactory(TranslatedTextRandomFactory):
    language = settings.LANGUAGE_CODE_EN


class OfferTranslatedTextFactory(TranslatedTextFactory):
    entity = entity_name.OFFER_YEAR


class GroupTranslatedTextFactory(TranslatedTextFactory):
    entity = entity_name.GROUP_YEAR


class LearningUnitYearTranslatedTextFactory(TranslatedTextFactory):
    entity = entity_name.LEARNING_UNIT_YEAR
