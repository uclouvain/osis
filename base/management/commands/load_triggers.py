import os

from base.management.commands.load_sql_scripts import LoadSqlCommand


class Command(LoadSqlCommand):
    subfolder_script_name = "triggers/"
    tablename_regex = r'ON.*(public..*)\n.*FOR'

    def __init__(self):
        super().__init__()
        self.lock_file = self.backoffice + self.subfolder_script_name + self.lock_file

    def handle(self, *args, **kwargs):
        self.load_triggers()

    def load_triggers(self):
        trigger_files = self._get_trigger_files()
        print("## Loading triggers from {} ##".format(self.scripts_path))
        for trigger_filename in trigger_files:
            self.load_trigger(trigger_filename)
        print("## Loading triggers finished ##")

    def _get_trigger_files(self):
        trigger_files = [
            file_name for file_name in os.listdir(self.scripts_path) if file_name not in self.files_to_ignore
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
