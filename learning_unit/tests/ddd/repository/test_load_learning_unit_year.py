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

from typing import List

from django.test import TestCase
from django.test.utils import override_settings

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.business.learning_unit import CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN, CMS_LABEL_SPECIFICATIONS, \
    CMS_LABEL_PEDAGOGY_FORCE_MAJEURE
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_achievement import LearningAchievementFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from cms.tests.factories.text_label import LearningUnitYearTextLabelFactory
from cms.tests.factories.translated_text import LearningUnitYearTranslatedTextFactory
from learning_unit.ddd.repository.load_learning_unit_year import load_multiple_by_identity
from learning_unit.tests.ddd.factories.learning_unit_year_identity import LearningUnitYearIdentityFactory
from reference.tests.factories.language import EnglishLanguageFactory, FrenchLanguageFactory

LANGUAGE_EN = "en"
LANGUAGE_FR = "fr-be"


class TestLoadLearningUnitVolumes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.l_unit_1 = LearningUnitYearFactory()
        cls.l_identity = LearningUnitYearIdentityFactory(
            code=cls.l_unit_1.acronym,
            year=cls.l_unit_1.academic_year.year
        )
        cls.practical_volume = PracticalLearningComponentYearFactory(learning_unit_year=cls.l_unit_1,
                                                                     hourly_volume_total_annual=20,
                                                                     hourly_volume_partial_q1=15,
                                                                     hourly_volume_partial_q2=5,
                                                                     planned_classes=1
                                                                     )
        cls.lecturing_volume = LecturingLearningComponentYearFactory(learning_unit_year=cls.l_unit_1,
                                                                     hourly_volume_total_annual=40,
                                                                     hourly_volume_partial_q1=20,
                                                                     hourly_volume_partial_q2=20,
                                                                     planned_classes=2
                                                                     )

    def test_load_learning_unit_year_init_volumes(self):
        results = load_multiple_by_identity([self.l_identity])
        self._assert_volume(results[0].practical_volume, self.practical_volume)
        self._assert_volume(results[0].lecturing_volume, self.lecturing_volume)

    def _assert_volume(self, volumes, expected):
        self.assertEqual(volumes.total_annual, expected.hourly_volume_total_annual)
        self.assertEqual(volumes.first_quadrimester, expected.hourly_volume_partial_q1)
        self.assertEqual(volumes.second_quadrimester, expected.hourly_volume_partial_q2)
        self.assertEqual(volumes.classes_count, expected.planned_classes)


class TestLoadLearningUnitEntities(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()

        cls.requirement_entity_version = EntityVersionFactory(acronym='DRT',
                                                              start_date=cls.academic_year.start_date)
        cls.allocation_entity_version = EntityVersionFactory(acronym='FIAL',
                                                             start_date=cls.academic_year.start_date)
        cls.l_unit_1 = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__requirement_entity=cls.requirement_entity_version.entity,
            learning_container_year__allocation_entity=cls.allocation_entity_version.entity,
        )
        cls.l_identity = LearningUnitYearIdentityFactory(
            code=cls.l_unit_1.acronym,
            year=cls.l_unit_1.academic_year.year
        )

    def test_load_learning_unit_year_init_entities(self):
        results = load_multiple_by_identity([self.l_identity])
        self.assertEqual(results[0].entities.requirement_entity_acronym, self.requirement_entity_version.acronym)
        self.assertEqual(results[0].entities.allocation_entity_acronym, self.allocation_entity_version.acronym)


class TestLoadLearningUnitDescriptionFiche(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.l_unit_1 = LearningUnitYearFactory()
        cls.l_identity = LearningUnitYearIdentityFactory(
            code=cls.l_unit_1.acronym,
            year=cls.l_unit_1.academic_year.year
        )
        dict_labels = {}
        for cms_label in CMS_LABEL_PEDAGOGY + CMS_LABEL_SPECIFICATIONS + CMS_LABEL_PEDAGOGY_FORCE_MAJEURE:
            dict_labels.update(
                {cms_label: LearningUnitYearTextLabelFactory(order=1, label=cms_label)}
            )

        cls.fr_cms_label = _build_cms_translated_text(
            cls.l_unit_1.id, dict_labels, LANGUAGE_FR,
            CMS_LABEL_PEDAGOGY + CMS_LABEL_SPECIFICATIONS + CMS_LABEL_PEDAGOGY_FORCE_MAJEURE
        )
        cls.en_cms_label = _build_cms_translated_text(
            cls.l_unit_1.id, dict_labels, LANGUAGE_EN,
            CMS_LABEL_PEDAGOGY_FR_AND_EN + CMS_LABEL_SPECIFICATIONS + CMS_LABEL_PEDAGOGY_FORCE_MAJEURE
        )

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_load_description_fiche(self):
        results = load_multiple_by_identity([self.l_identity])
        description_fiche = results[0].description_fiche

        self.assertEqual(description_fiche.resume, self.fr_cms_label.get('resume').text)
        self.assertEqual(description_fiche.teaching_methods, self.fr_cms_label.get('teaching_methods').text)
        self.assertEqual(description_fiche.evaluation_methods, self.fr_cms_label.get('evaluation_methods').text)
        self.assertEqual(description_fiche.other_informations, self.fr_cms_label.get('other_informations').text)
        self.assertEqual(description_fiche.online_resources, self.fr_cms_label.get('online_resources').text)
        self.assertEqual(description_fiche.bibliography, self.fr_cms_label.get('bibliography').text)
        self.assertEqual(description_fiche.mobility, self.fr_cms_label.get('mobility').text)

        self.assertEqual(description_fiche.resume_en, self.en_cms_label.get('resume').text)
        self.assertEqual(description_fiche.teaching_methods_en, self.en_cms_label.get('teaching_methods').text)
        self.assertEqual(description_fiche.evaluation_methods_en, self.en_cms_label.get('evaluation_methods').text)
        self.assertEqual(description_fiche.other_informations_en, self.en_cms_label.get('other_informations').text)
        self.assertEqual(description_fiche.online_resources_en, self.en_cms_label.get('online_resources').text)

        self.assertIsNone(description_fiche.last_update)
        self.assertIsNone(description_fiche.author)

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_load_specifications(self):
        results = load_multiple_by_identity([self.l_identity])
        description_fiche = results[0].specifications

        self.assertEqual(description_fiche.themes_discussed, self.fr_cms_label.get('themes_discussed').text)
        self.assertEqual(description_fiche.prerequisite, self.fr_cms_label.get('prerequisite').text)

        self.assertEqual(description_fiche.themes_discussed_en, self.en_cms_label.get('themes_discussed').text)
        self.assertEqual(description_fiche.prerequisite_en, self.en_cms_label.get('prerequisite').text)

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_load_force_majeure(self):
        results = load_multiple_by_identity([self.l_identity])
        force_majeure = results[0].force_majeure

        self.assertEqual(force_majeure.teaching_methods, self.fr_cms_label.get('teaching_methods_force_majeure').text)
        self.assertEqual(
            force_majeure.evaluation_methods, self.fr_cms_label.get('evaluation_methods_force_majeure').text
        )
        self.assertEqual(
            force_majeure.other_informations, self.fr_cms_label.get('other_informations_force_majeure').text
        )

        self.assertEqual(
            force_majeure.teaching_methods_en, self.en_cms_label.get('teaching_methods_force_majeure').text
        )
        self.assertEqual(
            force_majeure.evaluation_methods_en, self.en_cms_label.get('evaluation_methods_force_majeure').text
        )
        self.assertEqual(
            force_majeure.other_informations_en, self.en_cms_label.get('other_informations_force_majeure').text
        )

        self.assertIsNone(force_majeure.last_update)
        self.assertIsNone(force_majeure.author)


def _build_cms_translated_text(l_unit_id, dict_labels, language, cms_labels):
    translated_text_by_language = {}
    for cms_label in cms_labels:
        cms_text_label = dict_labels.get(cms_label)
        translated_text_by_language.update({
            cms_label: LearningUnitYearTranslatedTextFactory(text_label=cms_text_label,
                                                             reference=l_unit_id,
                                                             language=language,
                                                             text="Text {} {}".format(language, cms_label))
        })
    return translated_text_by_language


class TestLoadLearningUnitProposal(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()

        cls.l_unit_1 = LearningUnitYearFactory()
        cls.l_identity = LearningUnitYearIdentityFactory(
            code=cls.l_unit_1.acronym,
            year=cls.l_unit_1.academic_year.year
        )
        cls.proposal = ProposalLearningUnitFactory(learning_unit_year=cls.l_unit_1)

    def test_load_learning_unit_year_init_proposal(self):
        results = load_multiple_by_identity([self.l_identity])
        self.assertEqual(results[0].proposal.type, self.proposal.type)
        self.assertEqual(results[0].proposal.state, self.proposal.state)


class TestLoadLearningUnitYearWithAttribution(TestCase):

    @classmethod
    def setUpTestData(cls):
        academic_year = AcademicYearFactory(current=True)
        cls.l_unit_1 = LearningUnitYearFactory(
            acronym="LBIR1212",
            academic_year=academic_year,
            subtype=learning_unit_year_subtypes.FULL
        )
        component = LearningComponentYearFactory(learning_unit_year=cls.l_unit_1)

        cls.attribution_charge_news = _build_attributions(component)

        cls.l_unit_no_attribution = LearningUnitYearFactory(
            acronym="LBIR1213",
            academic_year=academic_year,
            subtype=learning_unit_year_subtypes.FULL
        )
        cls.l_unit_1_identity = LearningUnitYearIdentityFactory(code=cls.l_unit_1.acronym,
                                                                year=cls.l_unit_1.academic_year.year)
        cls.l_unit_no_attribution_identity = LearningUnitYearIdentityFactory(
            code=cls.l_unit_no_attribution.acronym,
            year=cls.l_unit_no_attribution.academic_year.year
        )
        cls.l_units_identities = [cls.l_unit_1_identity, cls.l_unit_no_attribution_identity]

    def test_load_learning_unit_year_result_count_correct(self):
        # def test_load_learning_unit_year_init_attributions(self):
        results = load_multiple_by_identity([self.l_unit_1_identity])
        self.assertEqual(len(results), 1)
        results = load_multiple_by_identity(self.l_units_identities)
        self.assertEqual(len(results), 2)

    def test_load_learning_unit_year_attributions_no_results(self):
        results = load_multiple_by_identity([self.l_unit_no_attribution_identity])
        self.assertEqual(len(results[0].attributions), 0)

    def test_load_learning_unit_year_attributions_content_and_order(self):
        results = load_multiple_by_identity([self.l_unit_1_identity])
        self.assertTrue(isinstance(results, List))

        attributions = results[0].attributions

        teacher_attribution = attributions[0].teacher
        self.assertEqual(teacher_attribution.last_name, "Marchal")
        self.assertEqual(teacher_attribution.first_name, "Cali")
        self.assertIsNone(teacher_attribution.middle_name)
        self.assertEqual(teacher_attribution.email, "cali@gmail.com")

        teacher_attribution = attributions[1].teacher
        self.assertEqual(teacher_attribution.last_name, "Marchal")
        self.assertEqual(teacher_attribution.first_name, "Tilia")
        self.assertIsNone(teacher_attribution.middle_name)
        self.assertEqual(teacher_attribution.email, "tilia@gmail.com")


def _build_attributions(component):
    attribution_1 = AttributionChargeNewFactory(learning_component_year=component,
                                                attribution__tutor__person__last_name='Marchal',
                                                attribution__tutor__person__first_name='Tilia',
                                                attribution__tutor__person__email='tilia@gmail.com')

    attribution_2 = AttributionChargeNewFactory(learning_component_year=component,
                                                attribution__tutor__person__last_name='Marchal',
                                                attribution__tutor__person__first_name='Cali',
                                                attribution__tutor__person__email='cali@gmail.com')
    return [attribution_1, attribution_2]


class TestLoadLearningUnitYearWithAchievements(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.l_unit_1 = LearningUnitYearFactory()
        cls.l_identity = LearningUnitYearIdentityFactory(
            code=cls.l_unit_1.acronym,
            year=cls.l_unit_1.academic_year.year
        )
        cls.en_language = EnglishLanguageFactory()
        cls.fr_language = FrenchLanguageFactory()
        # /!\ An achievement have the same code_name in EN and in FR
        cls.achievements_en = [LearningAchievementFactory(code_name='A_{}'.format(idx),
                                                          language=cls.en_language,
                                                          text="English text {}".format(idx),
                                                          learning_unit_year=cls.l_unit_1) for idx in range(5)]
        cls.achievements_fr = [LearningAchievementFactory(code_name='A_{}'.format(idx),
                                                          language=cls.fr_language,
                                                          text="French text {}".format(idx),
                                                          learning_unit_year=cls.l_unit_1) for idx in range(5)]

    def test_load_achievements(self):
        results = load_multiple_by_identity([self.l_identity])
        ue = results[0]
        self.assertEqual(len(ue.achievements), 5)

    def test_load_achievements_check_order(self):
        results = load_multiple_by_identity([self.l_identity])
        ue = results[0]
        for idx in range(5):
            self.assertEqual(ue.achievements[idx].text_fr, "French text {}".format(idx))
            self.assertEqual(ue.achievements[idx].text_en, "English text {}".format(idx))
