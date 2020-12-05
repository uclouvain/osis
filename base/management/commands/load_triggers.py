import os
import re

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    triggers_path = 'backoffice/triggers/'
    lock_file = 'lock.sql'
    files_to_ignore = [
        lock_file
    ]

    def handle(self, *args, **kwargs):
        print("##### Starting loading triggers from {} #####".format(self.triggers_path))
        lock_string = self.load_lock()
        self.load_triggers(self.triggers_path, lock_string)

    def load_lock(self):
        lock_path = self.triggers_path + self.lock_file
        return self._get_sql_string_from_file(path=lock_path)

    @staticmethod
    def _get_sql_string_from_file(path: str):
        file_extension = path.split(".")[-1].lower()
        if file_extension != 'sql':
            print("##### Error: Should load sql file but it is a {} extension".format(file_extension))
        file = open(path)
        return file.read()

    def load_triggers(self, path: str, lock_string: str):
        cursor = connection.cursor()
        for trigger_filename in os.listdir(path):
            if trigger_filename not in self.files_to_ignore:
                trigger_string = self._get_sql_string_from_file(path=path + trigger_filename)
                table_name = re.search(r'ON.*(public..*)\n.*FOR', trigger_string, re.IGNORECASE).group(1)
                sql_script = lock_string.format(
                    table_name=table_name,
                    trigger_sql=trigger_string
                )
                print("#### Load trigger from {filename} and lock table {tablename} ####".format(
                    filename=trigger_filename,
                    tablename=table_name
                ))
                cursor.execute(sql_script)
                print("#### Table {tablename} unlocked ####".format(
                    tablename=table_name
                ))
        print("##### Loading triggers finished #####")
