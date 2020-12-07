BEGIN WORK;
LOCK TABLE {table_to_lock} IN {lock_mode} MODE;
{sql_script}
COMMIT WORK;