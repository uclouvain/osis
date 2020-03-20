import rules
from django.test import SimpleTestCase

from osis_role.contrib import models as osis_role_models
from education_group.auth.roles.faculty_manager import FacultyManager


class TestFacultyManager(SimpleTestCase):
    def test_class_inherit_from_entity_role_model(self):
        self.assertTrue(issubclass(FacultyManager, osis_role_models.EntityRoleModel))

    def test_assert_group_name_meta_property(self):
        instance = FacultyManager()
        self.assertEquals(instance._meta.group_name, "faculty_manager")

    def test_assert_rule_sets_class_method(self):
        self.assertIsInstance(
            FacultyManager.rule_set(),
            rules.RuleSet
        )
