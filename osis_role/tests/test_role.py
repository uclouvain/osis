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
import mock
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from osis_role.contrib import models
from osis_role.role import OsisRoleManager


class TestOsisRoleManager(SimpleTestCase):
    def setUp(self):
        self.manager = OsisRoleManager()

    def test_register_case_not_subclass_of_role_model(self):
        class DummyObj(object):
            pass

        with self.assertRaises(ImproperlyConfigured):
            self.manager.register(DummyObj)

    def test_register_case_subclass_of_role_model(self):
        class RoleModelSubclass(models.RoleModel):
            class Meta:
                group_name = 'role_model_subclass'

        self.manager.register(RoleModelSubclass)
        self.assertIsInstance(self.manager.roles, set)
        self.assertEquals(len(self.manager.roles), 1)

    @mock.patch('osis_role.role.OsisRoleManager.roles', new_callable=mock.PropertyMock)
    def test_get_group_names_managed(self, mock_roles_set):
        class RoleModelSubclass(models.RoleModel):
            class Meta:
                group_name = 'role_model_subclass'
        mock_roles_set.return_value = {RoleModelSubclass}

        self.assertEquals(
            self.manager.group_names_managed(),
            {'role_model_subclass'}
        )
