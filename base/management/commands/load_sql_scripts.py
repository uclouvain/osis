import os
import re
from typing import List

from django.core.management.base import BaseCommand
from django.db import connection


class LoadSqlCommand(BaseCommand):
    backoffice: str = 'backoffice/'
    scripts_path = ''
    lock_file: str = 'lock.sql'
    lock_string: str = """"""
    files_to_ignore: List[str] = [
        lock_file
    ]
    cursor = None
    subfolder_script_name: str = ''
    tablename_regex: str = ''

    def __init__(self):
        super().__init__()
        self.scripts_path = self.backoffice + self.subfolder_script_name
        self.lock_string = self.load_lock()
        self.cursor = connection.cursor()

    def load_lock(self):
        return self._get_sql_string_from_file(file=self.lock_file)

    def _get_table_name(self, sql_string: str):
        table_name = re.search(self.tablename_regex, sql_string, re.IGNORECASE).group(1)
        return table_name

    def _get_sql_string_from_file(self, file: str):
        file_extension = file.split(".")[-1].lower()
        if file_extension != 'sql':
            print("##### Error: Should load sql file but it is a {} extension".format(file_extension))
        else:
            file = open(self.scripts_path + file)
            return file.read()

    def _get_scripts_files(self):
        scripts_files = [
            file_name for file_name in os.listdir(self.scripts_path) if file_name not in self.files_to_ignore
        ]
        return scripts_files
