import os
import re
import sys
from typing import Dict, List

import attr
from django.db import connection

LOCK_TEMPLATE = """
    BEGIN WORK;
    LOCK TABLE {table_to_lock} IN {lock_mode} MODE;
    {sql_script}
    COMMIT WORK;
"""


@attr.s()
class SQLLockStatement:
    lock_template = attr.ib(type=str, default=LOCK_TEMPLATE)
    lock_mode = attr.ib(type=str, default=None)


@attr.s()
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


class LoadSQL(SQLLockStatement, LoadSQLFilesToExecute):
    backoffice: str = 'backoffice/'
    cursor = None
    tablename_regex = None

    def __init__(self):
        super().__init__()
        self.cursor = connection.cursor()

    def _get_table_name(self, sql_string: str):
        table_match = re.search(self.tablename_regex, sql_string, re.IGNORECASE)
        try:
            match = table_match.group(1)
            if match:
                return match
        except Exception:
            sys.exit("#### Error: Unable to get table name from sql file ####")


class LoadSQLTriggers(LoadSQL):

    def __init__(self):
        self.subfolder = 'triggers/'
        self.scripts_path = self.backoffice + self.subfolder
        self.tablename_regex = r'CREATE TRIGGER[\S\s]*(public..*)'
        super().__init__()
        self.lock_mode = 'SHARE ROW EXCLUSIVE'

    def load_triggers(self):
        trigger_strings = self.load_scripts()
        print("## Loading triggers from {} ##".format(self.scripts_path))
        for trigger in trigger_strings:
            self.load_trigger(trigger)
        print("## Loading triggers finished ##")

    def load_trigger(self, trigger: Dict[str, str]):
        table_name = self._get_table_name(trigger['script_string'])
        print("YOLOOO", self.lock_mode)
        sql_script = self.lock_template.format(
            table_to_lock=table_name,
            sql_script=trigger['script_string'],
            lock_mode=self.lock_mode
        )
        print("# Load trigger from {filename} #".format(filename=trigger['filename']))
        print("# Table {tablename} LOCKED #".format(tablename=table_name))
        self.cursor.execute(sql_script)
        print("# Table {tablename} UNLOCKED #".format(tablename=table_name))
