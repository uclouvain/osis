import os

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        triggers_path = 'backoffice/triggers/'
        print("##### Starting loading triggers from {} #####".format(triggers_path))
        self.load_triggers(triggers_path)

    @staticmethod
    def load_triggers(path: str):
        cursor = connection.cursor()
        for trigger_file in os.listdir(path):
            sql_file = open(path + trigger_file)
            sql_as_string = sql_file.read()
            print("#### Load {} ####".format(trigger_file))
            cursor.execute(sql_as_string)
