##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.enums import academic_calendar_type
from base.models.enums.education_group_types import GroupType
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory, CloseAcademicCalendarFactory
from base.tests.factories.person import PersonFactory
from education_group.forms.group import GroupUpdateForm, GroupForm
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from education_group.tests.factories.auth.faculty_manager import FacultyManagerFactory


class TestGroupForm(TestCase):
    def setUp(self) -> None:
        for year in range(2020, 2025):
            OpenAcademicCalendarFactory(
                data_year__year=year,
                reference=academic_calendar_type.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT
            )
        CloseAcademicCalendarFactory(
            data_year__year=2026,
            reference=academic_calendar_type.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT
        )

        OpenAcademicCalendarFactory(data_year__year=2021, reference=academic_calendar_type.EDUCATION_GROUP_EDITION)
        CloseAcademicCalendarFactory(data_year__year=2022, reference=academic_calendar_type.EDUCATION_GROUP_EDITION)

    def test_assert_academic_years_available_for_faculty_manager(self):
        faculty_manager = FacultyManagerFactory()
        form = GroupForm(user=faculty_manager.person.user, group_type=GroupType.COMMON_CORE.name)

        self.assertQuerysetEqual(
            form.fields['academic_year'].queryset,
            [2021],
            transform=lambda obj: obj.year
        )

    def test_assert_academic_years_available_for_central_manager(self):
        central_manager = CentralManagerFactory()
        form = GroupForm(user=central_manager.person.user, group_type=GroupType.COMMON_CORE.name)

        self.assertQuerysetEqual(
            form.fields['academic_year'].queryset,
            [2020, 2021, 2022, 2023, 2024],
            transform=lambda obj: obj.year
        )


class TestGroupUpdateForm(TestCase):
    def setUp(self) -> None:
        self.person = PersonFactory()
        self.form = GroupUpdateForm(user=self.person.user, group_type=GroupType.COMMON_CORE.name)

    def test_assert_code_is_disabled(self):
        self.assertTrue(self.form.fields['code'].disabled)
        self.assertFalse(self.form.fields['code'].required)

    def test_assert_academic_year_is_disabled(self):
        self.assertTrue(self.form.fields['academic_year'].disabled)
        self.assertFalse(self.form.fields['academic_year'].required)
