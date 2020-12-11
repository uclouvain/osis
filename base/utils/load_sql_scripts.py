import logging
import os
import re
import sys
from typing import Dict, List

import attr
from django.conf import settings
from django.db import connection

logger = logging.getLogger(settings.DEFAULT_LOGGER)

SQLStringStatement = str
Filename = str

LOCK_TEMPLATE = """
    BEGIN WORK;
    LOCK TABLE {table_to_lock} IN {lock_mode} MODE;
    {sql_script}
    COMMIT WORK;
"""


@attr.s(frozen=True, slots=True)
class SQLLockStatement:
    lock_template = attr.ib(type=SQLStringStatement, default=LOCK_TEMPLATE)
    lock_mode = attr.ib(type=str, default=None)

    def add_lock_statement(self, sql_script: SQLStringStatement, table_name: str) -> SQLStringStatement:
        return self.lock_template.format(
            table_to_lock=table_name,
            sql_script=sql_script,
            lock_mode=self.lock_mode
        )


@attr.s(frozen=True, slots=True)
class LoadSQLFilesToExecute:
    subfolder = attr.ib(type=str, default=None)
    backoffice = attr.ib(type=str, default='backoffice/')
    scripts_path = attr.ib(type=str)

    @scripts_path.default
    def _scripts_path(self) -> str:
        return self.backoffice + self.subfolder

    def _get_scripts_files(self) -> List[Filename]:
        return os.listdir(self.scripts_path)

    def _get_sql_string_statement_from_file(self, filename: Filename) -> SQLStringStatement:
        file_extension = filename.split(".")[-1].lower()
        if file_extension != 'sql':
            logger.error("##### Should load sql file but it is a {} extension #####".format(file_extension))
            sys.exit()

        file = open(self.scripts_path + filename)
        return file.read()

    def load_scripts(self) -> Dict[Filename, SQLStringStatement]:
        script_filenames = self._get_scripts_files()
        script_strings = {}
        for script_filename in script_filenames:
            script_string = self._get_sql_string_statement_from_file(filename=script_filename)
            script_strings.update({script_filename: script_string})
        return script_strings


@attr.s(frozen=True, slots=True)
class ExecuteSQL:
    cursor = attr.ib()

    @cursor.default
    def _cursor(self):
        return connection.cursor()

    def execute(self, script: SQLStringStatement):
        self.cursor.execute(script)


@attr.s(frozen=True, slots=True)
class ExecuteSQLTriggers:
    loadSQLFile = attr.ib(type=LoadSQLFilesToExecute, default=LoadSQLFilesToExecute(subfolder='triggers/'))
    SQLLock = attr.ib(type=SQLLockStatement, default=SQLLockStatement(lock_mode='SHARE ROW EXCLUSIVE'))
    executeSQL = attr.ib(type=ExecuteSQL)

    @executeSQL.default
    def _executeSQL(self):
        return ExecuteSQL()

    def load_triggers(self):
        trigger_strings = self.loadSQLFile.load_scripts()
        logger.info("## Loading triggers from {} ##".format(self.loadSQLFile.scripts_path))
        for filename, trigger_script in trigger_strings.items():
            self.load_trigger(script=trigger_script, filename=filename)
        logger.info("## Loading triggers finished ##")

    def load_trigger(self, script: SQLStringStatement, filename: Filename):
        table_name = self._get_table_name(script)
        sql_script = self.SQLLock.add_lock_statement(
            sql_script=script,
            table_name=table_name
        )
        logger.info("# Load trigger from {filename} #".format(filename=filename))
        logger.info("# Table {tablename} LOCKED #".format(tablename=table_name))
        self.executeSQL.execute(sql_script)
        logger.info("# Table {tablename} UNLOCKED #".format(tablename=table_name))

    @staticmethod
    def _get_table_name(sql_string: SQLStringStatement) -> str:
        tablename_regex = r'CREATE TRIGGER[\S\s]*(public..*)'
        table_match = re.search(tablename_regex, sql_string, re.IGNORECASE)
        try:
            match = table_match.group(1)
            if match:
                return match
        except Exception:
            logger.error("#### Unable to get table name from sql file ####")
            sys.exit()
