import rules
from django.db import models
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from osis_common.models.serializable_model import SerializableModelAdmin
from osis_role.contrib import admin as osis_role_admin
from osis_role.contrib import models as osis_role_models


class EntityManagerAdmin(VersionAdmin, SerializableModelAdmin, osis_role_admin.EntityRoleModelAdmin):
    list_display = ('person', 'structure', 'entity')
    search_fields = ['person__first_name', 'person__last_name', 'structure__acronym']


class EntityManager(osis_role_models.EntityRoleModel):
    structure = models.ForeignKey('Structure', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Entity manager")
        verbose_name_plural = _("Entity managers")
        group_name = "entity_managers"

    def __str__(self):
        return u"%s" % self.person

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            "view_educationgroup": rules.always_allow,
            "change_scoresresponsible": rules.always_allow,
            "view_scoresresponsible": rules.always_allow,
            "change_programmanager": rules.always_allow,
            "view_programmanager": rules.always_allow,
            "can_access_catalog": rules.always_allow,
            "is_institution_administrator": rules.always_allow,
        })


def get_perms(model):
    return model._meta.permissions


def find_by_user(a_user, with_entity_version=True):
    qs = EntityManager.objects.filter(person__user=a_user) \
        .select_related('person', 'structure', 'entity') \
        .order_by('structure__acronym')
    if with_entity_version:
        qs = qs.prefetch_related(
            Prefetch('entity__entityversion_set', to_attr='entity_versions')
        )
    return qs


def find_entities_with_descendants_from_entity_managers(entities_manager, entities_by_id):
    entities_with_descendants = []
    for entity_manager in entities_manager:
        entities_with_descendants.append(entity_manager.entity)
        entities_with_descendants += [
            ent_version.entity for ent_version in entities_by_id[entity_manager.entity_id].get('all_children')
        ]
    return entities_with_descendants
