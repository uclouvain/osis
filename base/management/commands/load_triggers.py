from django.core.management.base import BaseCommand

from base.management.commands.load_sql_scripts import LoadSQLTriggers


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        LoadSQLTriggers().load_triggers()
