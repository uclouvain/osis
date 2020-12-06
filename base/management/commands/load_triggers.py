import os
import re

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    triggers_path = 'backoffice/triggers/'
    lock_file = 'lock.sql'
    lock_string = """"""
    files_to_ignore = [
        lock_file
    ]
    cursor = None

    def __init__(self):
        super().__init__()
        self.lock_string = self.load_lock()
        self.cursor = connection.cursor()

    def handle(self, *args, **kwargs):
        self.load_triggers()

    def load_lock(self):
        lock_path = self.triggers_path + self.lock_file
        return self._get_sql_string_from_file(path=lock_path)

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

    def load_trigger(self, trigger_filename):
        trigger_string = self._get_sql_string_from_file(path=self.triggers_path + trigger_filename)
        table_name = re.search(r'ON.*(public..*)\n.*FOR', trigger_string, re.IGNORECASE).group(1)
        sql_script = self.lock_string.format(
            table_name=table_name,
            trigger_sql=trigger_string
        )
        print("# Load trigger from {filename} #".format(filename=trigger_filename))
        print("# Table {tablename} LOCKED #".format(tablename=table_name))
        self.cursor.execute(sql_script)
        print("# Table {tablename} UNLOCKED #".format(
            tablename=table_name
        ))

    @staticmethod
    def _get_sql_string_from_file(path: str):
        file_extension = path.split(".")[-1].lower()
        if file_extension != 'sql':
            print("##### Error: Should load sql file but it is a {} extension".format(file_extension))
        file = open(path)
        return file.read()
