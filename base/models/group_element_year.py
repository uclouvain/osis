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
from collections import Counter

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, connection
from django.db.models import Q
from django.utils import translation
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel
from reversion.admin import VersionAdmin

from backoffice.settings.base import LANGUAGE_CODE_EN
from base.models.education_group_year import EducationGroupYear
from base.models.enums import quadrimesters
from base.models.enums.education_group_types import GroupType, MiniTrainingType
from base.models.enums.link_type import LinkTypes
from osis_common.models.osis_model_admin import OsisModelAdmin


class GroupElementYearAdmin(VersionAdmin, OsisModelAdmin):
    list_display = ('parent', 'child_branch', 'child_leaf',)
    readonly_fields = ('order',)
    search_fields = [
        'child_branch__acronym',
        'child_branch__partial_acronym',
        'child_leaf__acronym',
        'parent__acronym',
        'parent__partial_acronym'
    ]
    list_filter = ('is_mandatory', 'access_condition', 'parent__academic_year')


def validate_block_value(value):
    max_authorized_value = 6
    _error_msg = _("Please register a maximum of %(max_authorized_value)s digits in ascending order, "
                   "without any duplication. Authorized values are from 1 to 6. Examples: 12, 23, 46") %\
        {'max_authorized_value': max_authorized_value}

    MinValueValidator(1, message=_error_msg)(value)
    if not all([
        _check_integers_max_authorized_value(value, max_authorized_value),
        _check_integers_duplications(value),
        _check_integers_orders(value),
    ]):
        raise ValidationError(_error_msg)


def _check_integers_max_authorized_value(value, max_authorized_value):
    return all(int(char) <= max_authorized_value for char in str(value))


def _check_integers_duplications(value):
    if any(integer for integer, occurence in Counter(str(value)).items() if occurence > 1):
        return False
    return True


def _check_integers_orders(value):
    digit_values = [int(char) for char in str(value)]
    return list(sorted(digit_values)) == digit_values


class GroupElementYearManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            Q(child_branch__isnull=False) | Q(child_leaf__learning_container_year__isnull=False)
        )

    def get_adjacency_list(self, root_elements_ids):
        if not isinstance(root_elements_ids, list):
            raise Exception('root_elements_ids must be an instance of list')
        if not root_elements_ids:
            return []

        adjacency_query = """
            WITH RECURSIVE
                adjacency_query AS (
                    SELECT
                        parent_id as starting_node_id,
                        id,
                        child_branch_id,
                        child_leaf_id,
                        parent_id,
                        "order",
                        0 AS level,
                        CAST(parent_id || '|' ||
                            (
                                CASE
                                WHEN child_branch_id is not null
                                    THEN child_branch_id
                                    ELSE child_leaf_id
                                END
                            ) as varchar(1000)
                        ) As path
                    FROM base_groupelementyear
                    WHERE parent_id IN (%s)

                    UNION ALL

                    SELECT parent.starting_node_id,
                           child.id,
                           child.child_branch_id,
                           child.child_leaf_id,
                           child.parent_id,
                           child.order,
                           parent.level + 1,
                           CAST(
                                parent.path || '|' ||
                                    (
                                        CASE
                                        WHEN child.child_branch_id is not null
                                            THEN child.child_branch_id
                                            ELSE child.child_leaf_id
                                        END
                                    ) as varchar(1000)
                               ) as path
                    FROM base_groupelementyear AS child
                    INNER JOIN adjacency_query AS parent on parent.child_branch_id = child.parent_id
                )
            SELECT * FROM adjacency_query
            LEFT JOIN base_learningunityear bl on bl.id = adjacency_query.child_leaf_id
            WHERE adjacency_query.child_leaf_id is null or bl.learning_container_year_id is not null 
            ORDER BY starting_node_id, level, "order";
        """ % ','.join(["%s"] * len(root_elements_ids))

        with connection.cursor() as cursor:
            cursor.execute(adjacency_query, root_elements_ids)
            return [
                {
                    'starting_node_id': row[0],
                    'id': row[1],
                    'child_branch_id': row[2],
                    'child_leaf_id': row[3],
                    'parent_id': row[4],
                    'child_id': row[2] or row[3],
                    'order': row[5],
                    'level': row[6],
                    'path': row[7],
                } for row in cursor.fetchall()
            ]

    def get_root_list(
            self,
            child_leaf_ids=None,
            child_branch_ids=None,
            academic_year_id=None,
            link_type: LinkTypes = None,
            root_category_name=None
    ):
        root_category_name = root_category_name or []
        child_leaf_ids = child_leaf_ids or []
        child_branch_ids = child_branch_ids or []
        if child_leaf_ids and not isinstance(child_leaf_ids, list):
            raise Exception('child_leaf_ids must be an instance of list')
        if child_branch_ids and not isinstance(child_branch_ids, list):
            raise Exception('child_branch_ids must be an instance of list')
        if not child_leaf_ids and not child_branch_ids and not academic_year_id:
            return []

        # TODO :: simplify the code (by using a param child_ids_instance=LearningUnitYear by default?)
        where_statement = self._build_where_statement(academic_year_id, child_branch_ids, child_leaf_ids)
        reverse_adjacency_query = """
            WITH RECURSIVE
                root_query AS (
                    SELECT
                        CASE
                            WHEN gey.child_leaf_id is not null then gey.child_leaf_id
                            ELSE gey.child_branch_id
                            END as starting_node_id,
                        gey.id,
                        gey.child_branch_id,
                        gey.child_leaf_id,
                        gey.parent_id,
                        edyp.academic_year_id,
                        CASE
                            WHEN egt.name in (%(root_category_name)s) THEN true
                            ELSE false
                          END as is_root_row
                    FROM base_groupelementyear gey
                    INNER JOIN base_educationgroupyear AS edyp on gey.parent_id = edyp.id
                    INNER JOIN base_educationgrouptype AS egt on edyp.education_group_type_id = egt.id
                    LEFT JOIN base_learningunityear bl on gey.child_leaf_id = bl.id
                    LEFT JOIN base_educationgroupyear AS edyc on gey.parent_id = edyc.id
                    WHERE %(where_statement)s
                    AND (%(link_type)s IS NULL or gey.link_type = %(link_type)s)

                    UNION ALL

                    SELECT 	child.starting_node_id,
                      parent.id,
                      parent.child_branch_id,
                      parent.child_leaf_id,
                      parent.parent_id,
                      edyp.academic_year_id,
                      CASE
                        WHEN egt.name in (%(root_category_name)s) THEN true
                        ELSE false
                      END as is_root_row
                    FROM base_groupelementyear AS parent
                    INNER JOIN root_query AS child on parent.child_branch_id = child.parent_id and child.is_root_row = false
                    INNER JOIN base_educationgroupyear AS edyp on parent.parent_id = edyp.id
                    INNER JOIN base_educationgrouptype AS egt on edyp.education_group_type_id = egt.id
                )

            SELECT distinct starting_node_id, parent_id
            FROM root_query
            WHERE (%(academic_year_id)s IS NULL OR academic_year_id = %(academic_year_id)s) and (is_root_row is not Null and is_root_row = true)
            ORDER BY starting_node_id;
        """ % {
            'where_statement': where_statement,
            'academic_year_id': "%s",
            'link_type': '%s',
            'root_category_name': ', '.join(["'{}'".format(name) for name in root_category_name])
        }
        with connection.cursor() as cursor:
            parameters =  child_leaf_ids + child_branch_ids + [
                link_type.name if link_type else None,
                link_type.name if link_type else None,
                academic_year_id,
                academic_year_id
            ]
            cursor.execute(reverse_adjacency_query, parameters)
            return [
                {
                    'starting_node_id': row[0],
                    'root_id': row[1],
                } for row in cursor.fetchall()
            ]

    def _build_where_statement(self, academic_year_id, child_branch_ids, child_leaf_ids):
        where_statement_leaf = ""
        if child_leaf_ids:
            where_statement_leaf = "child_leaf_id in (%(child_ids)s)" % {
                'child_ids': ','.join(["%s"] * len(child_leaf_ids))
            }
        where_statement_branch = ""
        if child_branch_ids:
            where_statement_branch = "child_branch_id in (%(child_ids)s)" % {
                'child_ids': ','.join(["%s"] * len(child_branch_ids))
            }
        where_statement_academic_year = "(edyc.academic_year_id = {academic_year_id} " \
                                        "OR bl.academic_year_id = {academic_year_id})".format(
                                            academic_year_id=academic_year_id
                                        )
        if child_leaf_ids and child_branch_ids:
            where_statement = where_statement_leaf + ' OR ' + where_statement_branch
        elif child_leaf_ids and not child_branch_ids:
            where_statement = where_statement_leaf
        elif academic_year_id:
            where_statement = where_statement_academic_year
        else:
            where_statement = where_statement_branch
        return where_statement

    def get_reverse_adjacency_list(
            self,
            child_leaf_ids=None,
            child_branch_ids=None,
            academic_year_id=None,
            link_type: LinkTypes = None
    ):
        child_leaf_ids = child_leaf_ids or []
        child_branch_ids = child_branch_ids or []
        if child_leaf_ids and not isinstance(child_leaf_ids, list):
            raise Exception('child_leaf_ids must be an instance of list')
        if child_branch_ids and not isinstance(child_branch_ids, list):
            raise Exception('child_branch_ids must be an instance of list')
        if not child_leaf_ids and not child_branch_ids:
            return []

        where_statement = self._build_where_statement(None, child_branch_ids, child_leaf_ids)

        reverse_adjacency_query = """
            WITH RECURSIVE
                reverse_adjacency_query AS (
                    SELECT
                        CASE
                            WHEN gey.child_leaf_id is not null then gey.child_leaf_id
                            ELSE gey.child_branch_id
                        END as starting_node_id,
                           gey.id,
                           gey.child_branch_id,
                           gey.child_leaf_id,
                           gey.parent_id,
                           gey.order,
                           edyc.academic_year_id,
                           0 AS level
                    FROM base_groupelementyear gey
                    INNER JOIN base_educationgroupyear AS edyc on gey.parent_id = edyc.id
                    WHERE %(where_statement)s
                    AND (%(link_type)s IS NULL or gey.link_type = %(link_type)s)

                    UNION ALL

                    SELECT 	child.starting_node_id,
                            parent.id,
                            parent.child_branch_id,
                            parent.child_leaf_id,
                            parent.parent_id,
                            parent.order,
                            edyp.academic_year_id,
                            child.level + 1
                    FROM base_groupelementyear AS parent
                    INNER JOIN reverse_adjacency_query AS child on parent.child_branch_id = child.parent_id
                    INNER JOIN base_educationgroupyear AS edyp on parent.parent_id = edyp.id
                )

            SELECT distinct starting_node_id, id, child_branch_id, child_leaf_id, parent_id, "order", level
            FROM reverse_adjacency_query
            WHERE %(academic_year_id)s IS NULL OR academic_year_id = %(academic_year_id)s
            ORDER BY starting_node_id,  level DESC, "order";
        """ % {
            'where_statement': where_statement,
            'academic_year_id': "%s",
            'link_type': '%s',
        }
        with connection.cursor() as cursor:
            parameters = child_leaf_ids + child_branch_ids + [
                link_type.name if link_type else None,
                link_type.name if link_type else None,
                academic_year_id,
                academic_year_id
            ]
            cursor.execute(reverse_adjacency_query, parameters)
            return [
                {
                    'starting_node_id': row[0],
                    'id': row[1],
                    'child_branch_id': row[2],
                    'child_leaf_id': row[3],
                    'parent_id': row[4],
                    'child_id': row[2] or row[3],
                    'order': row[5],
                    'level': row[6],
                } for row in cursor.fetchall()
            ]


class GroupElementYear(OrderedModel):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    parent = models.ForeignKey(
        EducationGroupYear,
        null=True,  # TODO: can not be null, dirty data
        on_delete=models.PROTECT,
    )

    child_branch = models.ForeignKey(
        EducationGroupYear,
        related_name='child_branch',  # TODO: can not be child_branch
        blank=True, null=True,
        on_delete=models.CASCADE,
    )

    child_leaf = models.ForeignKey(
        'LearningUnitYear',
        related_name='child_leaf',  # TODO: can not be child_leaf
        blank=True, null=True,
        on_delete=models.CASCADE,
    )

    relative_credits = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("relative credits"),
    )

    min_credits = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Min. credits"),
    )

    max_credits = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Max. credits"),
    )

    is_mandatory = models.BooleanField(
        default=True,
        verbose_name=_("Mandatory"),
    )

    block = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Block"),
        validators=[validate_block_value]
    )

    access_condition = models.BooleanField(
        default=False,
        verbose_name=_('Access condition')
    )

    comment = models.TextField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("comment"),
    )
    comment_english = models.TextField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("english comment"),
    )

    own_comment = models.CharField(max_length=500, blank=True, null=True)

    quadrimester_derogation = models.CharField(
        max_length=10,
        choices=quadrimesters.DEROGATION_QUADRIMESTERS,
        blank=True, null=True, verbose_name=_('Quadrimester derogation')
    )

    link_type = models.CharField(
        max_length=25,
        choices=LinkTypes.choices(),
        blank=True, null=True, verbose_name=_('Link type')
    )

    order_with_respect_to = 'parent'

    objects = GroupElementYearManager()

    def __str__(self):
        return "{} - {}".format(self.parent, self.child)

    @property
    def verbose_comment(self):
        if self.comment_english and translation.get_language() == LANGUAGE_CODE_EN:
            return self.comment_english
        return self.comment

    class Meta:
        unique_together = (('parent', 'child_branch'), ('parent', 'child_leaf'))
        ordering = ('order',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.clean()
        return super().save(force_insert, force_update, using, update_fields)

    # FIXME :: DEPRECATED ??? Move this to validators? (is a model validation - not a business validation?)
    # FIXME :: Should be moved to form validation via validators of the ddd module
    def clean(self):
        if self.child_branch and self.child_leaf:
            raise ValidationError(_("It is forbidden to save a GroupElementYear with a child branch and a child leaf."))

        if self.child_branch == self.parent:
            raise ValidationError(_("It is forbidden to add an element to itself."))

        if self.parent and self.child_branch in self.parent.ascendants_of_branch:
            raise ValidationError(_("It is forbidden to add an element to one of its included elements."))

        if self.child_leaf and self.link_type == LinkTypes.REFERENCE.name:
            raise ValidationError(
                {'link_type': _("You are not allowed to create a reference with a learning unit")}
            )
        self._check_same_academic_year_parent_child_branch()

    # FIXME :: DEPRECATED -  Use AttachOptionsValidator
    def _check_same_academic_year_parent_child_branch(self):
        if (self.parent and self.child_branch) and \
                (self.parent.academic_year.year != self.child_branch.academic_year.year):
            raise ValidationError(_("It is prohibited to attach a group, mini-training or training to an element of "
                                    "another academic year."))

        self._clean_link_type()

    def _clean_link_type(self):
        if getattr(self.parent, 'type', None) in [GroupType.MINOR_LIST_CHOICE.name,
                                                  GroupType.MAJOR_LIST_CHOICE.name] and \
           isinstance(self.child, EducationGroupYear) and self.child.type in MiniTrainingType.minors() + \
                [MiniTrainingType.FSA_SPECIALITY.name, MiniTrainingType.DEEPENING.name]:
            self.link_type = LinkTypes.REFERENCE.name

    @cached_property
    def child(self):
        return self.child_branch or self.child_leaf


def fetch_row_sql(root_ids):
    return GroupElementYear.objects.get_adjacency_list(root_ids)