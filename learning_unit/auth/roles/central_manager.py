import rules
from django.utils.translation import gettext_lazy as _

from osis_role.contrib import admin as osis_role_admin
from osis_role.contrib import models as osis_role_models


class CentralManagerAdmin(osis_role_admin.EntityRoleModelAdmin):
    list_display = osis_role_admin.EntityRoleModelAdmin.list_display


class CentralManager(osis_role_models.EntityRoleModel):
    class Meta:
        default_related_name = 'learning_unit'
        verbose_name = _("Central manager")
        verbose_name_plural = _("Central managers")
        group_name = "central_managers_for_ue"

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
        })
