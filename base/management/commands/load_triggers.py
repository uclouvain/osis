from django.core.management.base import BaseCommand

from base.management.commands.load_sql_scripts import ExecuteSQLTriggers


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        ExecuteSQLTriggers().load_triggers()
