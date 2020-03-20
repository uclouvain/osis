import rules
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from education_group.auth import scope
from osis_role.contrib import models as osis_role_models
from osis_role.contrib import admin as osis_role_admin


class FacultyManagerAdmin(osis_role_admin.EntityRoleModelAdmin):
    list_display = osis_role_admin.EntityRoleModelAdmin.list_display + ('scopes', )


class FacultyManager(osis_role_models.EntityRoleModel):
    scopes = ArrayField(
        models.CharField(max_length=200, choices=scope.Scope.choices()),
        blank=True,
    )

    class Meta:
        verbose_name = _("Faculty manager")
        verbose_name_plural = _("Faculty managers")
        group_name = "faculty_manager"  # TODO: Must be renamed in faculty_managers after complete migration

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({})
