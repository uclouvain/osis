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
from django.core.management import BaseCommand
from openpyxl import load_workbook
from django.apps import apps


class Command(BaseCommand):

    def handle(self, *args, **options):
        apps.clear_cache()
        workbook = load_workbook("fixtures_to_load.xlsx", read_only=True, data_only=True)
        for ws in workbook.worksheets:
            app_name = ws.title.split('.')[0]
            model_name = ws.title.split('.')[1]
            model_class = apps.get_model(app_name, model_name)
            xls_rows = list(ws.rows)
            headers = [(idx, cell.value) for idx, cell in enumerate(xls_rows[0])]
            for row in xls_rows[1:]:
                object_as_dict = {
                    column_name: row[idx].value for idx, column_name in headers
                }
                object_dict_with_relations = {
                    fk_field_name: value_as_obj
                    for fk_field_name, value_as_obj in [
                        self.recur(model_class, col_name, value) for col_name, value in object_as_dict.items()
                    ]
                }
                obj, created = model_class.objects.get_or_create(**object_dict_with_relations)
                print('Object < {} > successfully {}'.format(obj, 'created' if created else 'updated'))

    def recur(self, model_class, col_name, value, recur=0) -> object:
        foreign_key_field = col_name
        if '__' in col_name:
            splitted_col_name = col_name.split('__')
            foreign_key_field = splitted_col_name[0]
            if foreign_key_field in [f.name for f in model_class._meta.fields]:
                field = model_class._meta.get_field(foreign_key_field)
                if field.is_relation:
                    _, related_obj = self.recur(
                        field.related_model,
                        '__'.join(splitted_col_name[1:]),
                        value,
                        recur=recur+1
                    )
                    value = related_obj
            else:
                foreign_key_field = col_name
        if recur == 0:
            return foreign_key_field, value
        return foreign_key_field, model_class.objects.get(**{foreign_key_field: value})
