from django.core.management.base import BaseCommand

from base.management.commands.load_sql_scripts import LoadSQLTriggers


class Command(LoadSQLTriggers, BaseCommand):

    def handle(self, *args, **kwargs):
        self.load_triggers()
