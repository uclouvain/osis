import rules
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _, pgettext

from base.models.enums.education_group_categories import Categories
from education_group.auth import predicates
from education_group.auth.scope import Scope
from osis_role.contrib import models as osis_role_models
from osis_role.contrib import admin as osis_role_admin
from osis_role.contrib import predicates as osis_role_predicates


class FacultyManagerAdmin(osis_role_admin.EntityRoleModelAdmin):
    list_display = osis_role_admin.EntityRoleModelAdmin.list_display + ('scopes', )


class FacultyManager(osis_role_models.EntityRoleModel):
    scopes = ArrayField(
        models.CharField(max_length=200, choices=Scope.choices()),
        blank=True,
    )

    class Meta:
        verbose_name = _("Faculty manager")
        verbose_name_plural = _("Faculty managers")
        group_name = "faculty_manager"  # TODO: Must be renamed in faculty_managers after complete migration

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'view_educationgroup': rules.always_allow,
            'add_training': osis_role_predicates.always_deny(
                message=pgettext("female", "The user has not permission to create a %(category)s.") %
                {"category": Categories.TRAINING.value}
            ),
            'add_minitraining':
                predicates.is_program_edition_period_open &
                predicates.is_maximum_child_not_reached_for_mini_training_category
            ,
            'add_group':
                predicates.is_not_orphan_group &
                predicates.is_program_edition_period_open &
                predicates.is_maximum_child_not_reached_for_group_category
            ,
            'change_educationgroup':
                predicates.is_education_group_year_older_or_equals_than_limit_settings_year &
                predicates.is_education_group_type_authorized_according_to_user_scope &
                predicates.is_user_link_to_management_entity &
                predicates.is_program_edition_period_open,
            'delete_all_educationgroup':
                predicates.is_all_education_group_are_removable,
            'delete_educationgroup':
                predicates.is_user_link_to_management_entity &
                predicates.is_program_edition_period_open,
            'attach_educationgroup':
                predicates.is_education_group_year_older_or_equals_than_limit_settings_year &
                predicates.is_education_group_type_authorized_according_to_user_scope &
                predicates.is_user_link_to_management_entity &
                predicates.is_program_edition_period_open,
            'detach_educationgroup':
                predicates.is_education_group_year_older_or_equals_than_limit_settings_year &
                predicates.is_education_group_type_authorized_according_to_user_scope &
                predicates.is_user_link_to_management_entity &
                predicates.is_program_edition_period_open,
        })

    def get_allowed_education_group_types(self):
        allowed_education_group_types = []
        for scope in self.scopes:
            allowed_education_group_types += Scope.get_education_group_types(scope)
        return allowed_education_group_types
