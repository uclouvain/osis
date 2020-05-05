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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test.utils import override_settings
from django.test import TestCase

from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from cms.enums import entity_name
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from learning_unit.ddd.repository.load_learning_unit_year import load_multiple
from reference.tests.factories.language import FrenchLanguageFactory, EnglishLanguageFactory
from base.business.learning_unit import CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN, CMS_LABEL_SPECIFICATIONS
from unittest import mock


class TestLoadLearningUnitDescriptionFiche(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.en_language = EnglishLanguageFactory()
        cls.fr_language = FrenchLanguageFactory()

        cls.l_unit_1 = LearningUnitYearFactory()
        print('ID {}'.format(cls.l_unit_1.id))

        text_label_lu_3 = TextLabelFactory(order=1, label='resume', entity=entity_name.LEARNING_UNIT_YEAR)

        TranslatedTextFactory(text_label=text_label_lu_3,
                              entity=entity_name.LEARNING_UNIT_YEAR,
                              reference=cls.l_unit_1.id,
                              language=cls.fr_language.code,
                              text="Text fr")
        TranslatedTextFactory(text_label=text_label_lu_3,
                              entity=entity_name.LEARNING_UNIT_YEAR,
                              reference=cls.l_unit_1.id,
                              language=cls.en_language.code,
                              text="Text en")

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    @mock.patch("learning_unit.ddd.repository.load_achievement.load_achievements")
    def test_load_resume(self, mock=True):
        print('test_load_resume')
        print(self.l_unit_1.id)
        for r in TranslatedTextLabel.objects.all():
            print('for1')
            print(r.label)
        for r in TranslatedText.objects.all():
            print('for2')
            print("{} {} . referrence{}".format(r.text_label.label, r.text, r.reference))
        results = load_multiple([self.l_unit_1.id])
        print('*********************************')
        ##TODO resume est tj nul???
        print(results[0].description_fiche.__dict__)
        print('*************')
