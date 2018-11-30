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
from django.db.models import QuerySet
from django.test import TestCase

from base.tests.factories.education_group_achievement import EducationGroupAchievementFactory
from base.tests.factories.education_group_detailed_achievement import EducationGroupDetailedAchievementFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from cms.enums import entity_name
from cms.tests.factories.translated_text import TranslatedTextFactory
from webservices import business


class EnsureKeyTestCase(TestCase):
    def test_skills_and_achievement_key(self):
        self.assertEqual(business.SKILLS_AND_ACHIEVEMENTS_KEY, 'comp_acquis')

    def test_skills_and_achievement_data(self):
        self.assertEqual(business.SKILLS_AND_ACHIEVEMENTS_AA_DATA, 'achievements')

    def test_evaluation_key(self):
        self.assertEqual(business.EVALUATION_KEY, 'evaluation')


class GetAchievementsTestCase(TestCase):
    def setUp(self):
        self.education_group_year = EducationGroupYearFactory()
        self.education_group_achievement = EducationGroupAchievementFactory(
            education_group_year=self.education_group_year
        )
        self.education_group_detailed_achievement = EducationGroupDetailedAchievementFactory(
            education_group_achievement=self.education_group_achievement
        )

    def test_get_achievements_case_get_english_version(self):
        qs = business.get_achievements(self.education_group_year, settings.LANGUAGE_CODE_EN)

        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 1)

        achievement = qs.first()
        self.assertEqual(achievement.text, self.education_group_achievement.english_text)
        self.assertTrue(len(achievement.detailed_achievements), 1)

        detailed_achievement = achievement.detailed_achievements[0]
        self.assertEqual(detailed_achievement.text, self.education_group_detailed_achievement.english_text)

    def test_get_achievements_case_get_french_version(self):
        qs = business.get_achievements(self.education_group_year, settings.LANGUAGE_CODE_FR)

        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 1)

        achievement = qs.first()
        self.assertEqual(achievement.text, self.education_group_achievement.french_text)

        self.assertTrue(len(achievement.detailed_achievements), 1)
        detailed_achievement = achievement.detailed_achievements[0]
        self.assertEqual(detailed_achievement.text, self.education_group_detailed_achievement.french_text)

    def test_get_achievements_case_language_code_not_supported(self):
        with self.assertRaises(AttributeError):
            business.get_achievements(self.education_group_year, 'dummy-language')


class GetIntroExtraContentAchievementsTestCase(TestCase):
    def setUp(self):
        self.cms_label_name = 'skills_and_achievements_introduction'
        self.education_group_year = EducationGroupYearFactory()
        self.introduction = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.pk,
            language=settings.LANGUAGE_CODE_EN,
            text_label__label=self.cms_label_name
        )

    def test_get_achievements_case_get_english_version(self):
        intro_extra_content = business.get_intro_extra_content_achievements(
            self.education_group_year,
            settings.LANGUAGE_CODE_EN
        )

        self.assertIsInstance(intro_extra_content, dict)
        self.assertEqual(intro_extra_content[self.cms_label_name], self.introduction.text)

    def test_get_achievements_case_get_french_version_no_results(self):
        intro_extra_content = business.get_intro_extra_content_achievements(
            self.education_group_year,
            settings.LANGUAGE_CODE_FR
        )
        self.assertIsInstance(intro_extra_content, dict)
        self.assertDictEqual(intro_extra_content, {})


class GetEvaluationTestCase(TestCase):
    def setUp(self):
        self.education_group_year = EducationGroupYearFactory()
        self.cms_label_name = 'evaluation'
        self.evaluation = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.pk,
            language=settings.LANGUAGE_CODE_FR,
            text_label__label=self.cms_label_name,
            text_label__entity=entity_name.OFFER_YEAR
        )

    def test_get_evaluation_french_version(self):
        label, text = business.get_evaluation_text(self.education_group_year, settings.LANGUAGE_CODE_FR)
        self.assertEqual(text, self.evaluation.text)

    def test_get_evaluation_no_english_version(self):
        label, text = business.get_evaluation_text(self.education_group_year, settings.LANGUAGE_CODE_EN)
        self.assertEqual(text, '')
        self.assertEqual(label, '')
