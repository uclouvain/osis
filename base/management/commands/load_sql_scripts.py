import os
import re
import sys
from typing import Dict, List

import attr
from django.core.management.base import BaseCommand
from django.db import connection

LOCK_TEMPLATE = """
    BEGIN WORK;
    LOCK TABLE {table_to_lock} IN {lock_mode} MODE;
    {sql_script}
    COMMIT WORK;
"""


class SQLLockStatement:
    lock_template = attr.ib(type=str, default=None)
    lock_mode = attr.ib(type=str, default=None)


class LoadSQLFilesToExecute:
    subfolder = attr.ib(type=str, default=None)
    scripts_path = attr.ib(type=str, default=None)

    def _get_scripts_files(self):
        return os.listdir(self.scripts_path)

    def _get_sql_string_from_file(self, file: str) -> str:
        file_extension = file.split(".")[-1].lower()
        if file_extension != 'sql':
            sys.exit("##### Error: Should load sql file but it is a {} extension".format(file_extension))

        file = open(self.scripts_path + file)
        return file.read()

    def load_scripts(self) -> List[Dict[str, str]]:
        script_filenames = self._get_scripts_files()
        script_strings = []
        for script_filename in script_filenames:
            script_string = self._get_sql_string_from_file(file=script_filename)
            script_strings.append(
                {'script_string': script_string, 'filename': script_filename}
            )
        return script_strings


class LoadSqlCommand(BaseCommand, SQLLockStatement, LoadSQLFilesToExecute):
    backoffice: str = 'backoffice/'
    cursor = None
    tablename_regex = None

    def __init__(self):
        super().__init__()
        self.scripts_path = self.backoffice + self.subfolder
        self.lock_template = LOCK_TEMPLATE
        self.cursor = connection.cursor()

    def _get_table_name(self, sql_string: str):
        table_match = re.search(self.tablename_regex, sql_string, re.IGNORECASE)
        try:
            match = table_match.group(1)
            if match:
                return match
        except Exception:
            sys.exit("#### Error: Unable to get table name from sql file ####")

