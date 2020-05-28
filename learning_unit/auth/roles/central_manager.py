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
            'base.can_create_learningunit': rules.always_allow,
            'base.can_access_learningunit': rules.always_allow,
            'base.can_delete_learningunit': rules.always_allow,
            'base.can_edit_learningunit': rules.always_allow,
            'base.add_externallearningunityear': rules.always_allow,
            'base.can_propose_learningunit': rules.always_allow,
            'base.can_edit_learningunit_date': rules.always_allow,
            'base.can_edit_learningunit_pedagogy': rules.always_allow,
            'base.can_edit_learningunit_specification': rules.always_allow,
            'base.can_consolidate_learningunit_proposal': rules.always_allow,
        })
