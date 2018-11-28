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
from django.test import TestCase
from django.utils.translation import gettext

from base.forms.learning_unit.simplified_volume import SimplifiedVolumeForm, SimplifiedVolumeManagementForm
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.models.learning_component_year import LearningComponentYear
from base.tests.factories.academic_year import get_current_year
from base.tests.factories.business.learning_units import GenerateContainer
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.person import PersonFactory


class TestSimplifiedVolumeManagementForm(TestCase):
    def setUp(self):
        self.data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '2',
            'form-0-hourly_volume_total_annual': 20,
            'form-0-hourly_volume_partial_q1': 10,
            'form-0-hourly_volume_partial_q2': 10,
            'form-1-hourly_volume_total_annual': 20,
            'form-1-hourly_volume_partial_q1': 10,
            'form-1-hourly_volume_partial_q2': 10,
        }
        generator = GenerateContainer(get_current_year(), get_current_year())
        self.learning_unit_year = generator[0].learning_unit_year_full
        self.entity_container_years = generator[0].list_repartition_volume_entities
        self.person = PersonFactory()

    def test_save(self):
        formset = SimplifiedVolumeManagementForm(self.data, self.person, queryset=LearningComponentYear.objects.none())
        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        cm_component = learning_component_years[0]
        tp_component = learning_component_years[1]

        self.assertEqual(cm_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)
        self.assertEqual(tp_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)

        self.assertEqual(cm_component.type, LECTURING)
        self.assertEqual(tp_component.type, PRACTICAL_EXERCISES)

        self.assertEqual(cm_component.entitycomponentyear_set.count(), 3)
        self.assertEqual(tp_component.entitycomponentyear_set.count(), 3)

    def test_save_with_master_thesis_container_type(self):
        formset = SimplifiedVolumeManagementForm(self.data, self.person, queryset=LearningComponentYear.objects.none())
        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        cm_component = learning_component_years[0]
        tp_component = learning_component_years[1]

        self.assertEqual(cm_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)
        self.assertEqual(tp_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)

        self.assertEqual(cm_component.type, LECTURING)
        self.assertEqual(tp_component.type, PRACTICAL_EXERCISES)

        self.assertEqual(cm_component.entitycomponentyear_set.count(), 3)
        self.assertEqual(tp_component.entitycomponentyear_set.count(), 3)

    def test_save_update(self):
        formset = SimplifiedVolumeManagementForm(
            self.data, self.person,
            queryset=LearningComponentYear.objects.filter(
                learningunitcomponent__learning_unit_year=self.learning_unit_year
            )
        )

        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        cm_component = learning_component_years[0]
        tp_component = learning_component_years[1]

        self.assertEqual(cm_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)
        self.assertEqual(tp_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)

        self.assertEqual(cm_component.type, LECTURING)
        self.assertEqual(tp_component.type, PRACTICAL_EXERCISES)

        self.assertEqual(cm_component.entitycomponentyear_set.count(), 3)
        self.assertEqual(tp_component.entitycomponentyear_set.count(), 3)

    def test_save_correct_planned_classes(self):
        strange_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '2',
            'form-0-hourly_volume_total_annual': 0,
            'form-0-hourly_volume_partial_q1': 0,
            'form-0-hourly_volume_partial_q2': 0,
            'form-1-hourly_volume_total_annual': 20,
            'form-1-hourly_volume_partial_q1': 10,
            'form-1-hourly_volume_partial_q2': 10,
        }

        formset = SimplifiedVolumeManagementForm(
            strange_data, self.person,
            queryset=LearningComponentYear.objects.none())
        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        component_with_volume_nul = learning_component_years[0]
        component_with_volume_not_null = learning_component_years[1]

        self.assertEqual(component_with_volume_nul.planned_classes, 0)
        self.assertEqual(component_with_volume_not_null.planned_classes, 1)


class TestSimplifiedVolumeForm(TestCase):
    def setUp(self):
        self.instance = LearningComponentYearFactory()

    def test_clean(self):
        self.instance.hourly_volume_partial_q1 = 0
        form = SimplifiedVolumeForm(
            data={"hourly_volume_partial_q1": 12}, is_faculty_manager=True, instance=self.instance,
            component_type=self.instance.type
        )
        form.is_valid()
        self.assertEqual(form.errors["hourly_volume_partial_q1"][0],
                         gettext("One of the partial volumes must have a value to 0."))
        self.assertEqual(form.errors["hourly_volume_partial_q2"][0],
                         gettext("One of the partial volumes must have a value to 0."))

        self.instance.hourly_volume_partial_q1 = 12
        form = SimplifiedVolumeForm(
            data={"hourly_volume_partial_q1": 0}, is_faculty_manager=True, instance=self.instance,
            component_type=self.instance.type
        )
        form.is_valid()
        self.assertEqual(form.errors["hourly_volume_partial_q1"][0],
                         gettext("The volume can not be set to 0."))
        self.assertFalse(form.errors.get("hourly_volume_partial_q2"))
