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
import uuid
from copy import deepcopy
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from base.forms.learning_unit_pedagogy import LearningUnitPedagogyEditForm, TeachingMaterialModelForm
from base.models.enums.learning_unit_year_subtypes import FULL
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.teaching_material import TeachingMaterialFactory
from cms.tests.factories.text_label import LearningUnitYearTextLabelFactory
from cms.tests.factories.translated_text import LearningUnitYearTranslatedTextFactory
from learning_unit.tests.factories.central_manager import CentralManagerFactory
from reference.tests.factories.language import EnglishLanguageFactory


class LearningUnitPedagogyContextMixin(TestCase):
    """"This mixin is used in this test file in order to setup an environment for testing pedagogy"""

    @classmethod
    def setUpTestData(cls):
        cls.language = EnglishLanguageFactory()
        cls.person = CentralManagerFactory().person
        cls.current_ac = AcademicYearFactory(current=True)
        cls.past_ac_years = AcademicYearFactory.produce_in_past(cls.current_ac.year - 1, 5)
        cls.future_ac_years = AcademicYearFactory.produce_in_future(cls.current_ac.year + 1, 5)

        cls.current_luy = LearningUnitYearFactory(
            learning_container_year__academic_year=cls.current_ac,
            academic_year=cls.current_ac,
            acronym="LAGRO1000",
            subtype=FULL
        )
        cls.luys = {cls.current_ac.year: cls.current_luy}
        cls.luys.update(
            _duplicate_learningunityears(cls.current_luy, academic_years=cls.past_ac_years + cls.future_ac_years)
        )


class TestValidation(LearningUnitPedagogyContextMixin):
    def setUp(self):
        super().setUp()
        self.cms_translated_text = LearningUnitYearTranslatedTextFactory(
            reference=self.luys[self.current_ac.year - 1].id,
            language='EN',
            text='Text random'
        )
        self.valid_form_data = _get_valid_cms_form_data(self.cms_translated_text)

    def test_invalid_form(self):
        del self.valid_form_data['cms_id']
        form = LearningUnitPedagogyEditForm(self.valid_form_data)
        self.assertFalse(form.is_valid())

    def test_valid_form(self):
        form = LearningUnitPedagogyEditForm(self.valid_form_data)
        self.assertEqual(form.errors, {})
        self.assertTrue(form.is_valid())

    @patch("cms.models.translated_text.update_or_create")
    def test_save_without_postponement(self, mock_update_or_create):
        """In this test, we ensure that if we modify UE of N-1 or N-... => The postponement is not done for CMS data"""
        form = LearningUnitPedagogyEditForm(self.valid_form_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        mock_update_or_create.assert_called_once_with(entity=self.cms_translated_text.entity,
                                                      reference=self.cms_translated_text.reference,
                                                      language=self.cms_translated_text.language,
                                                      text_label=self.cms_translated_text.text_label,
                                                      defaults={'text': self.cms_translated_text.text})

    @patch("cms.models.translated_text.update_or_create")
    def test_save_with_postponement(self, mock_update_or_create):
        """In this test, we ensure that if we modify UE of N or N+X => The postponement until the lastest UE"""
        luy_in_future = self.luys[self.current_ac.year + 1]
        cms_pedagogy_future = LearningUnitYearTranslatedTextFactory(
            reference=luy_in_future.id,
            language='EN',
            text='Text in future'
        )
        form = LearningUnitPedagogyEditForm(data=_get_valid_cms_form_data(cms_pedagogy_future))
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        # N+1 ===> N+6
        self.assertEqual(mock_update_or_create.call_count, 5)


class TestTeachingMaterialForm(LearningUnitPedagogyContextMixin):
    @patch('base.business.learning_units.pedagogy.postpone_teaching_materials', side_effect=lambda *args: None)
    def test_save_without_postponement(self, mock_postpone_teaching_materials):
        """In this test, we ensure that if we modify UE of N-1 or N-X => The postponement is not done for teaching
           materials"""
        luy_in_past = self.luys[self.current_ac.year - 1]
        teaching_material = TeachingMaterialFactory.build(learning_unit_year=luy_in_past,
                                                          mandatory=True)
        post_data = _get_valid_teaching_material_form_data(teaching_material)
        teaching_material_form = TeachingMaterialModelForm(post_data)
        self.assertTrue(teaching_material_form.is_valid(), teaching_material_form.errors)
        teaching_material_form.save(learning_unit_year=luy_in_past)
        self.assertFalse(mock_postpone_teaching_materials.called)

    @patch('base.business.learning_units.pedagogy.postpone_teaching_materials', side_effect=lambda *args: None)
    def test_save_with_postponement(self, mock_postpone_teaching_materials):
        """In this test, we ensure that if we modify UE of N or N+X => The postponement until the lastest UE"""
        luy_in_future = self.luys[self.current_ac.year + 1]
        teaching_material = TeachingMaterialFactory.build(learning_unit_year=luy_in_future, mandatory=True)
        post_data = _get_valid_teaching_material_form_data(teaching_material)
        teaching_material_form = TeachingMaterialModelForm(post_data)
        self.assertTrue(teaching_material_form.is_valid(), teaching_material_form.errors)
        teaching_material_form.save(learning_unit_year=luy_in_future)
        self.assertTrue(mock_postpone_teaching_materials.called)


class TestLearningUnitPedagogyEditForm(LearningUnitPedagogyContextMixin):
    @patch("cms.models.translated_text.update_or_create")
    def test_save_fr_bibliography_also_updates_en_bibliography(self, mock_update_or_create):
        """Ensure that if we modify bibliography in FR => bibliography in EN is updated with same text"""
        text_label_bibliography = LearningUnitYearTextLabelFactory(label='bibliography')
        cms_translated_text_fr = LearningUnitYearTranslatedTextFactory(
            reference=self.luys[self.current_ac.year].id,
            language='fr-be',
            text_label=text_label_bibliography,
            text='Some random text'
        )
        valid_form_data_fr = _get_valid_cms_form_data(cms_translated_text_fr)

        form = LearningUnitPedagogyEditForm(valid_form_data_fr)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        for language in settings.LANGUAGES:
            mock_update_or_create.assert_any_call(
                entity=cms_translated_text_fr.entity,
                reference=cms_translated_text_fr.reference,
                language=language[0],
                text_label=cms_translated_text_fr.text_label,
                defaults={'text': cms_translated_text_fr.text}
            )


def _duplicate_learningunityears(luy_to_duplicate, academic_years):
    # Duplicate learning unit year with different academic year
    luys = {}
    for ac_year in academic_years:
        new_luy = deepcopy(luy_to_duplicate)
        new_luy.pk = None
        new_luy.uuid = uuid.uuid4()
        new_luy.academic_year = ac_year
        new_luy.save()
        luys[ac_year.year] = new_luy
    return luys


def _get_valid_cms_form_data(cms_translated_text):
    """Valid data for form CMS form"""
    return {
        "trans_text": getattr(cms_translated_text, 'text'),
        "cms_id": getattr(cms_translated_text, 'id'),
        "reference": getattr(cms_translated_text, 'reference')
    }


def _get_valid_teaching_material_form_data(teaching_material):
    """Valid data for teaching material form"""
    data = {
        'title': teaching_material.title
    }
    if getattr(teaching_material, 'mandatory', False):
        data['mandatory'] = True
    return data
