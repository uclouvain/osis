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

from django.test import TestCase
from django.test.utils import override_settings

from base.business.learning_unit import CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN, CMS_LABEL_SPECIFICATIONS
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from cms.enums import entity_name
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from learning_unit.ddd.repository.load_learning_unit_year import load_multiple

LANGUAGE_EN = "en"
LANGUAGE_FR = "fr-be"


class TestLoadLearningUnitVolumes(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.l_unit_1 = LearningUnitYearFactory()
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
        results = load_multiple([self.l_unit_1.id])
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

    def test_load_learning_unit_year_init_entities(self):
        results = load_multiple([self.l_unit_1.id])
        self.assertEqual(results[0].entities.requirement_entity_acronym, self.requirement_entity_version.acronym)
        self.assertEqual(results[0].entities.allocation_entity_acronym, self.allocation_entity_version.acronym)


class TestLoadLearningUnitDescriptionFiche(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.l_unit_1 = LearningUnitYearFactory()
        dict_labels = {}
        for cms_label in CMS_LABEL_PEDAGOGY + CMS_LABEL_SPECIFICATIONS:
            dict_labels.update(
                {cms_label: TextLabelFactory(order=1, label=cms_label, entity=entity_name.LEARNING_UNIT_YEAR)}
            )

        cls.fr_cms_label = _build_cms_translated_text(cls.l_unit_1.id, dict_labels, LANGUAGE_FR,
                                                      CMS_LABEL_PEDAGOGY + CMS_LABEL_SPECIFICATIONS)
        cls.en_cms_label = _build_cms_translated_text(cls.l_unit_1.id, dict_labels, LANGUAGE_EN,
                                                      CMS_LABEL_PEDAGOGY_FR_AND_EN + CMS_LABEL_SPECIFICATIONS)

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_load_description_fiche(self):
        results = load_multiple([self.l_unit_1.id])
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

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_load_specifications(self):
        results = load_multiple([self.l_unit_1.id])
        description_fiche = results[0].specifications

        self.assertEqual(description_fiche.themes_discussed, self.fr_cms_label.get('themes_discussed').text)
        self.assertEqual(description_fiche.prerequisite, self.fr_cms_label.get('prerequisite').text)

        self.assertEqual(description_fiche.themes_discussed_en, self.en_cms_label.get('themes_discussed').text)
        self.assertEqual(description_fiche.prerequisite_en, self.en_cms_label.get('prerequisite').text)


def _build_cms_translated_text(l_unit_id, dict_labels, language, cms_labels):
    translated_text_by_language = {}
    for cms_label in cms_labels:
        cms_text_label = dict_labels.get(cms_label)
        translated_text_by_language.update({
            cms_label: TranslatedTextFactory(text_label=cms_text_label,
                                             entity=entity_name.LEARNING_UNIT_YEAR,
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
        cls.proposal = ProposalLearningUnitFactory(learning_unit_year=cls.l_unit_1)

    def test_load_learning_unit_year_init_proposal(self):
        results = load_multiple([self.l_unit_1.id])
        self.assertEqual(results[0].proposal.type, self.proposal.type)
        self.assertEqual(results[0].proposal.state, self.proposal.state)
