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
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag

from base.models.enums.link_type import LinkTypes
from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_year import GroupFactory, EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import PersonFactory
from base.utils.cache import ElementCache


@override_flag('education_group_update', active=True)
class TestMoveGroupElementYearView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.next_academic_year = AcademicYearFactory(current=True)
        cls.root_egy = EducationGroupYearFactory(academic_year=cls.next_academic_year)
        cls.group_element_year = GroupElementYearFactory(
            parent__academic_year=cls.next_academic_year,
            generate_element=True
        )
        cls.selected_egy = GroupFactory(
            academic_year=cls.next_academic_year
        )
        GroupElementYearFactory(parent=cls.root_egy, child_branch=cls.selected_egy, generate_element=True)

        path_to_attach = "|".join([str(cls.root_egy.pk), str(cls.selected_egy.pk)])
        cls.url = reverse("group_element_year_move", args=[cls.root_egy.id])
        cls.url = "{}?path={}".format(
            cls.url, path_to_attach
        )

        cls.person = PersonFactory()

    def setUp(self):
        self.client.force_login(self.person.user)

        permission_patcher = mock.patch.object(User, "has_perms")
        self.permission_mock = permission_patcher.start()
        self.permission_mock.return_value = True
        self.addCleanup(permission_patcher.stop)
        self.addCleanup(ElementCache(self.person.user).clear)

    def test_should_check_attach_and_detach_permission(self):
        AuthorizedRelationshipFactory(
            parent_type=self.selected_egy.education_group_type,
            child_type=self.group_element_year.child_branch.education_group_type,
            min_count_authorized=0,
            max_count_authorized=None
        )
        ElementCache(self.person.user.id).save_element_selected_bis(
            element_year=self.group_element_year.child_branch.academic_year.year,
            element_code=self.group_element_year.child_branch.partial_acronym,
            path_to_detach="|".join([str(self.group_element_year.parent.id), str(self.group_element_year.child_branch.id)]),
            action=ElementCache.ElementCacheAction.CUT
        )
        self.client.get(self.url)
        self.permission_mock.assert_has_calls(
            [
                mock.call(("base.detach_educationgroup",), self.group_element_year.parent),
                mock.call(("base.attach_educationgroup",), self.selected_egy)
            ]

        )
        self.assertTrue(self.permission_mock.called)

    def test_move(self):
        AuthorizedRelationshipFactory(
            parent_type=self.selected_egy.education_group_type,
            child_type=self.group_element_year.child_branch.education_group_type,
            min_count_authorized=0,
            max_count_authorized=None
        )
        ElementCache(self.person.user.id).save_element_selected_bis(
            element_year=self.group_element_year.child_branch.academic_year.year,
            element_code=self.group_element_year.child_branch.partial_acronym,
            path_to_detach="|".join([str(self.group_element_year.parent.id), str(self.group_element_year.child_branch.id)]),
            action=ElementCache.ElementCacheAction.CUT
        )

        self.client.post(self.url, data={
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
            "link_type": LinkTypes.REFERENCE.name
        })

        self.assertFalse(GroupElementYear.objects.filter(id=self.group_element_year.id).exists())
        self.assertTrue(
            GroupElementYear.objects.filter(
                parent=self.selected_egy,
                child_branch=self.group_element_year.child_branch
            ).exists()
        )
