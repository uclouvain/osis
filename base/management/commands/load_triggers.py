import os
import re
from typing import List

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    triggers_path: str = 'backoffice/triggers/'
    lock_file: str = 'lock.sql'
    lock_string: str = """"""
    files_to_ignore: List[str] = [
        lock_file
    ]
    cursor = None
    tablename_regex = r'ON.*(public..*)\n.*FOR'

    def __init__(self):
        super().__init__()
        self.lock_string = self.load_lock()
        self.cursor = connection.cursor()

    def handle(self, *args, **kwargs):
        self.load_triggers()

    def load_lock(self):
        return self._get_sql_string_from_file(file=self.lock_file)

    def load_triggers(self):
        trigger_files = self._get_trigger_files()
        print("## Loading triggers from {} ##".format(self.triggers_path))
        for trigger_filename in trigger_files:
            self.load_trigger(trigger_filename)
        print("## Loading triggers finished ##")

    def _get_trigger_files(self):
        trigger_files = [
            file_name for file_name in os.listdir(self.triggers_path) if file_name not in self.files_to_ignore
        ]
        return trigger_files

    def load_trigger(self, trigger_filename: str):
        trigger_string = self._get_sql_string_from_file(file=trigger_filename)
        table_name = self._get_table_name(trigger_string)
        sql_script = self.lock_string.format(
            table_name=table_name,
            trigger_sql=trigger_string
        )
        print("# Load trigger from {filename} #".format(filename=trigger_filename))
        print("# Table {tablename} LOCKED #".format(tablename=table_name))
        self.cursor.execute(sql_script)
        print("# Table {tablename} UNLOCKED #".format(tablename=table_name))

    def _get_table_name(self, sql_string: str):
        table_name = re.search(self.tablename_regex, sql_string, re.IGNORECASE).group(1)
        return table_name

    def _get_sql_string_from_file(self, file: str):
        file_extension = file.split(".")[-1].lower()
        if file_extension != 'sql':
            print("##### Error: Should load sql file but it is a {} extension".format(file_extension))
        file = open(self.triggers_path + file)
        return file.read()
