from base.management.commands.load_sql_scripts import LoadSqlCommand


class Command(LoadSqlCommand):
    subfolder = "triggers/"
    tablename_regex = r'ON.*(public..*)\n.*FOR'

    def handle(self, *args, **kwargs):
        self.load_triggers()

    def load_triggers(self):
        trigger_files = self._get_scripts_files()
        print("## Loading triggers from {} ##".format(self.scripts_path))
        for trigger_filename in trigger_files:
            self.load_trigger(trigger_filename)
        print("## Loading triggers finished ##")

    def load_trigger(self, trigger_filename: str):
        trigger_string = self._get_sql_string_from_file(file=trigger_filename)
        table_name = self._get_table_name(trigger_string)
        sql_script = self.lock_string.format(
            table_to_lock=table_name,
            sql_script=trigger_string
        )
        print("# Load trigger from {filename} #".format(filename=trigger_filename))
        print("# Table {tablename} LOCKED #".format(tablename=table_name))
        self.cursor.execute(sql_script)
        print("# Table {tablename} UNLOCKED #".format(tablename=table_name))
