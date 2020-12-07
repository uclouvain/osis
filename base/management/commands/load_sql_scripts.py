import os
import re
import sys
from typing import List

from django.core.management.base import BaseCommand
from django.db import connection


class LoadSqlCommand(BaseCommand):
    backoffice: str = 'backoffice/'
    scripts_path = ''
    lock_file: str = 'lock.sql'
    lock_string: str = """"""
    files_to_ignore: List[str] = [
        lock_file.lower()
    ]
    cursor = None
    subfolder: str = ''
    tablename_regex: str = ''

    def __init__(self):
        super().__init__()
        self.scripts_path = self.backoffice + self.subfolder
        self.lock_string = self.load_lock()
        self.cursor = connection.cursor()

    def load_lock(self):
        return self._get_sql_string_from_file(file=self.lock_file)

    def _get_table_name(self, sql_string: str):
        table_match = re.search(self.tablename_regex, sql_string, re.IGNORECASE)
        try:
            match = table_match.group(1)
            if match:
                return match
        except Exception:
            sys.exit("#### Error: Unable to get table name from sql file ####")

    def _get_sql_string_from_file(self, file: str):
        file_extension = file.split(".")[-1].lower()
        if file_extension != 'sql':
            sys.exit("##### Error: Should load sql file but it is a {} extension".format(file_extension))
        else:
            file = open(self.scripts_path + file)
            return file.read()

    def _get_scripts_files(self):
        scripts_files = [
            file_name for file_name in os.listdir(self.scripts_path) if file_name.lower() not in self.files_to_ignore
        ]
        return scripts_files
