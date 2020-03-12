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

from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from base.tests.factories.person import PersonFactory
from osis_role.contrib import models
from osis_role.tests.utils import ConcreteRoleModel


class TestRoleModel(TestCase):
    def setUp(self):
        self.person = PersonFactory()

    def test_ensure_class_is_abstract(self):
        instance = models.RoleModel()
        self.assertTrue(instance._meta.abstract)

    def test_ensure_concrete_class_must_define_group_name_property(self):
        with self.assertRaises(ImproperlyConfigured):
            class InvalidRoleModel(models.RoleModel):
                class Meta:
                    abstract = False
                    group_name = None

    @mock.patch('django.db.models.Model.save', return_value=None)
    @mock.patch('osis_role.contrib.models.RoleModel._add_user_to_group', return_value=None)
    def test_ensure_save_will_call_add_user_to_group_method(self, mock_model_save, mock_add_user_to_group):
        instance = ConcreteRoleModel(person=self.person)
        instance.save()

        self.assertTrue(mock_model_save.called)
        self.assertTrue(mock_add_user_to_group.called)

    @mock.patch('django.db.models.Model.delete', return_value=None)
    @mock.patch('osis_role.contrib.models.RoleModel._remove_user_from_group', return_value=None)
    def test_ensure_delete_will_call_remove_user_from_group_method(self, mock_model_delete, mock_remove_user_from_group):
        instance = ConcreteRoleModel(person=self.person)
        instance.delete()

        self.assertTrue(mock_model_delete.called)
        self.assertTrue(mock_remove_user_from_group.called)

    def test_ensure_add_user_to_group_will_create_group_if_not_exist_and_attach_user(self):
        instance = ConcreteRoleModel(person=self.person)
        instance._add_user_to_group()

        self.assertTrue(Group.objects.filter(name=ConcreteRoleModel.group_name).exists())
        self.assertIn(ConcreteRoleModel.group_name, self.person.user.groups.all().values_list('name', flat=True))

    @mock.patch('django.db.models.QuerySet.exists', return_value=False)
    def test_remove_user_to_group_case_not_more_record_in_table(self, mock_queryset_exists):
        group = Group.objects.create(name=ConcreteRoleModel.group_name)
        self.person.user.groups.add(group)

        instance = ConcreteRoleModel(person=self.person)
        instance._remove_user_from_group(self.person)
        self.assertNotIn(ConcreteRoleModel.group_name, self.person.user.groups.all().values_list('name', flat=True))

    @mock.patch('django.db.models.QuerySet.exists', return_value=True)
    def test_remove_user_to_group_case_have_still_one_record_in_table(self, mock_queryset_exists):
        group = Group.objects.create(name=ConcreteRoleModel.group_name)
        self.person.user.groups.add(group)

        instance = ConcreteRoleModel(person=self.person)
        instance._remove_user_from_group(self.person)
        self.assertIn(ConcreteRoleModel.group_name, self.person.user.groups.all().values_list('name', flat=True))

    @mock.patch('django.db.models.QuerySet.exists', return_value=True)
    def test_belong_to_case_person_belong_to_model(self, mock_queryset_exists):
        self.assertTrue(ConcreteRoleModel().belong_to(self.person))

    @mock.patch('django.db.models.QuerySet.exists', return_value=False)
    def test_belong_to_case_person_not_belong_to_model(self, mock_queryset_exists):
        self.assertFalse(ConcreteRoleModel().belong_to(self.person))
