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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import PersonFactory
from base.utils.cache import cache, ElementCache


class TestAttachTypeDialogView(TestCase):
    def setUp(self):
        self.group_element_year = GroupElementYearFactory()
        self.education_group_year = EducationGroupYearFactory(
            academic_year=self.group_element_year.parent.academic_year
        )

        self.url = reverse(
            "education_group_attach",
            args=[self.group_element_year.parent.id, self.group_element_year.child_branch.id]
        )

        self.person = PersonFactory()

        self.client.force_login(self.person.user)
        self.perm_patcher = mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group",
                                       return_value=True)
        self.mocked_perm = self.perm_patcher.start()

        self.addCleanup(self.mocked_perm.stop)
        self.addCleanup(cache.clear)

    def test_context_data(self):
        ElementCache(self.person.user).save_element_selected(self.education_group_year,
                                                             source_link_id=self.group_element_year.id)
        response = self.client.get(self.url)
        context = response.context

        self.assertEqual(context["object_to_attach"], self.education_group_year)
        self.assertEqual(context["source_link"], self.group_element_year)
        self.assertEqual(context["education_group_year_parent"], self.group_element_year.child_branch)
