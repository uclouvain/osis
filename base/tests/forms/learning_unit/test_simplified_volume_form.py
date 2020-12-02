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

from base.forms.learning_unit.edition_volume import SimplifiedVolumeForm, SimplifiedVolumeManagementForm
from base.models.enums.component_type import COMPONENT_TYPES
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.models.learning_component_year import LearningComponentYear
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.business.learning_units import GenerateContainer
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.person import PersonFactory
from learning_unit.tests.factories.central_manager import CentralManagerFactory


class TestSimplifiedVolumeManagementForm(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            'component-TOTAL_FORMS': '2',
            'component-INITIAL_FORMS': '0',
            'component-MAX_NUM_FORMS': '2',
            'component-0-hourly_volume_total_annual': 20,
            'component-0-hourly_volume_partial_q1': 10,
            'component-0-hourly_volume_partial_q2': 10,
            'component-1-hourly_volume_total_annual': 20,
            'component-1-hourly_volume_partial_q1': 10,
            'component-1-hourly_volume_partial_q2': 10,
            'component-0-planned_classes': 1,
            'component-1-planned_classes': 1,
        }
        current_academic_year = create_current_academic_year()
        generator = GenerateContainer(current_academic_year, current_academic_year)
        cls.learning_unit_year = generator[0].learning_unit_year_full
        cls.entity_container_years = generator[0].list_repartition_volume_entities
        cls.person = CentralManagerFactory().person

    def test_save(self):
        formset = SimplifiedVolumeManagementForm(self.data, self.person, queryset=LearningComponentYear.objects.none())
        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        cm_component = learning_component_years[0]
        tp_component = learning_component_years[1]

        self.assertEqual(cm_component.learning_unit_year, self.learning_unit_year)
        self.assertEqual(tp_component.learning_unit_year, self.learning_unit_year)

        self.assertEqual(cm_component.type, LECTURING)
        self.assertEqual(tp_component.type, PRACTICAL_EXERCISES)

    def test_save_update(self):
        formset = SimplifiedVolumeManagementForm(
            self.data, self.person,
            queryset=LearningComponentYear.objects.filter(learning_unit_year=self.learning_unit_year)
        )

        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        cm_component = learning_component_years[0]
        tp_component = learning_component_years[1]

        self.assertEqual(cm_component.learning_unit_year, self.learning_unit_year)
        self.assertEqual(tp_component.learning_unit_year, self.learning_unit_year)

        self.assertEqual(cm_component.type, LECTURING)
        self.assertEqual(tp_component.type, PRACTICAL_EXERCISES)


class TestSimplifiedVolumeForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.instance = LearningComponentYearFactory(
            hourly_volume_total_annual=10,
            hourly_volume_partial_q1=5,
            hourly_volume_partial_q2=5
        )
        cls.person = PersonFactory()

    def test_clean(self):
        self.instance.hourly_volume_partial_q1 = 0
        form = SimplifiedVolumeForm(
            data={"hourly_volume_partial_q1": 5}, is_faculty_manager=True, instance=self.instance,
            index=0,
            component_type=COMPONENT_TYPES[0],
            user=self.person.user,
        )
        form.is_valid()
        self.assertTrue(
            gettext("One of the partial volumes must have a value to 0.") in form.errors["hourly_volume_partial_q1"])
        self.assertTrue(
            gettext("One of the partial volumes must have a value to 0.") in form.errors["hourly_volume_partial_q2"])

        self.instance.hourly_volume_partial_q1 = 12
        form = SimplifiedVolumeForm(
            data={"hourly_volume_partial_q1": 0}, is_faculty_manager=True, instance=self.instance,
            component_type=COMPONENT_TYPES[0],
            index=0,
            user=self.person.user,
        )
        form.is_valid()
        self.assertTrue(gettext("The volume can not be set to 0.") in form.errors["hourly_volume_partial_q1"])
        self.assertFalse(form.errors.get("hourly_volume_partial_q2"))

        self.instance.hourly_volume_partial_q1 = 5
        self.instance.hourly_volume_partial_q2 = 12
        form = SimplifiedVolumeForm(
            data={"hourly_volume_partial_q2": 0}, is_faculty_manager=True, instance=self.instance,
            component_type=COMPONENT_TYPES[0],
            index=0,
            user=self.person.user,
        )
        form.is_valid()
        self.assertTrue(gettext("The volume can not be set to 0.") in form.errors["hourly_volume_partial_q2"])
        self.assertFalse(form.errors.get("hourly_volume_partial_q1"))

    def test_with_incorrect_volume_total(self):
        form = SimplifiedVolumeForm(
            data={"hourly_volume_partial_q1": 5, "hourly_volume_partial_q2": 7,
                  'hourly_volume_total_annual': 10}, is_faculty_manager=True, instance=self.instance,
            index=0,
            component_type=COMPONENT_TYPES[0],
            user=self.person.user,
        )
        form.is_valid()
        self.assertEqual(form.errors["hourly_volume_partial_q1"][0], gettext(""))
        self.assertEqual(form.errors["hourly_volume_partial_q2"][0], gettext(""))
        self.assertEqual(form.errors["hourly_volume_total_annual"][0],
                         gettext('The annual volume must be equal to the sum of the volumes Q1 and Q2'))
