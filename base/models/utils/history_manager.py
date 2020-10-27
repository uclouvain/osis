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
from typing import List, Optional, Dict, Tuple

from django.db import models


class HistoryManagerMixin(models.QuerySet):
    revision_query = """
        WITH last_update_info AS (
            SELECT upper(person.last_name) || ' ' || person.first_name as author, revision.date_created AS last_update
            FROM reversion_version version
            JOIN reversion_revision revision ON version.revision_id = revision.id
            JOIN auth_user users ON revision.user_id = users.id
            JOIN base_person person ON person.user_id = users.id
            join django_content_type ct on version.content_type_id = ct.id
            {left_joins}
            left join cms_translatedtext tt on cast(version.object_id as integer) = tt.id and ct.model = 'translatedtext'
            left join cms_textlabel tl on tt.text_label_id = tl.id
            left join base_teachingmaterial tm on cast(version.object_id as integer) = tm.id and ct.model = 'teachingmaterial'
            join base_learningunityear luy on luy.id = tm.learning_unit_year_id or luy.id = tt.reference
            {basic_where_clause}
            where "base_groupelementyear"."child_leaf_id" = luy.id
            and tl.label in {labels_to_check}
            order by revision.date_created desc limit 1
        )
    """

    select_query = """
        SELECT {field_to_select} FROM last_update_info
    """

    """
        :models_with_history: Dictionary with tables to get with left join as keys (ex: base_teachingmaterial)
        If the key has a value, it means that an extra left join has to be done to filter results in the where clause
        (ex: cms_translatedtext with extra left join cms_textlabel to filter on the label)
        The value is a Tuple with the table to get and the field to match (ex: ('cms_textlabel', 'text_label_id'))
        {
            'cms_translatedtext': ('cms_textlabel', 'text_label_id'),
            'base_teachingmaterial': None
        }
        will generate
            left join cms_translatedtext on cast(version.object_id as integer) = cms_translatedtext.id and ct.model = 'translatedtext'
            left join cms_textlabel on tt.text_label_id = cms_textlabel.id
            left join base_teachingmaterial on cast(version.object_id as integer) = base_teachingmaterial.id and ct.model = 'teachingmaterial'
    """
    def annotate_with_history(self, models_with_history: Dict[str, Optional[Tuple[str, str]]]):
        left_joins = '\n'.join([
            self.build_left_join_model_with_history(table_name, extra_parameters)
            for table_name, extra_parameters in models_with_history.items()
        ])
        self.revision_query = self.revision_query.format(
            left_joins=left_joins,
            basic_where_clause=,
        )

    def build_basic_where_clause(self, model_to_match_id: str, outerref_field: str):
        complete_model = self.model.__name__.split('.')[1:]
        current_model = '_'.join(complete_model[1:])
        return """
            where "{model_to_annotate}"."{outerref_field}" = {model_to_match}.id
        """.format(
            model_to_annotate=current_model,
            outerref_field=outerref_field,
            model_to_match=model_to_match_id
        )

    def build_left_join_model_with_history(self, table_to_get: str, extra_parameters: Optional[Tuple[str, str]]):
        model = table_to_get.split('_')[-1]
        left_join =  """
            left join {table_to_get} on cast(version.object_id as integer) = {table_to_get}.id and ct.model = '{model}' 
        """.format(
            table_to_get=table_to_get,
            model=model
        )
        if extra_parameters:
            extra_left_join = self._build_extra_left_join(table_to_match=table_to_get, parameters=extra_parameters)
            return '\n'.join([left_join, extra_left_join])
        return left_join

    @staticmethod
    def _build_extra_left_join(table_to_match: str, parameters: Tuple[str, str]):
        table_to_get, field_to_match = parameters
        return """
            left join {table_to_get} on {table_to_match}.{field_to_match} = {table_to_get}.id
        """.format(
            table_to_get=table_to_get,
            table_to_match=table_to_match,
            field_to_match=field_to_match
        )

    @staticmethod
    def build_extra_where_clause(possible_values: List[str], field_to_filter: str, table_to_filter: str):
        return """
            and {table_to_filter}.{field_to_filter} in {possible_values}
        """.format(
            possible_values=repr(tuple(map(str, possible_values))),
            table_to_filter=table_to_filter,
            field_to_filter=field_to_filter
        )