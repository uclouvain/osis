from typing import Dict

from base.management.commands.load_sql_scripts import LoadSqlCommand


class Command(LoadSqlCommand):

    def __init__(self):
        self.tablename_regex = r'CREATE TRIGGER[\S\s]*(public..*)'
        self.subfolder = 'triggers/'
        self.lock_mode = 'SHARE ROW EXCLUSIVE'
        super().__init__()

    def handle(self, *args, **kwargs):
        self.load_triggers()

    def load_triggers(self):
        trigger_strings = self.load_scripts()
        print("## Loading triggers from {} ##".format(self.scripts_path))
        for trigger in trigger_strings:
            self.load_trigger(trigger)
        print("## Loading triggers finished ##")

    def load_trigger(self, trigger: Dict[str, str]):
        table_name = self._get_table_name(trigger['script_string'])
        sql_script = self.lock_template.format(
            table_to_lock=table_name,
            sql_script=trigger['script_string'],
            lock_mode=self.lock_mode
        )
        print("# Load trigger from {filename} #".format(filename=trigger['filename']))
        print("# Table {tablename} LOCKED #".format(tablename=table_name))
        self.cursor.execute(sql_script)
        print("# Table {tablename} UNLOCKED #".format(tablename=table_name))
