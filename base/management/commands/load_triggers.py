from django.core.management.base import BaseCommand

from base.utils.load_sql_scripts import ExecuteSQLTriggers


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        ExecuteSQLTriggers().load_triggers()
