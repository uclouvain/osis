BEGIN WORK;
LOCK TABLE {table_to_lock} IN SHARE MODE;
{sql_script}
COMMIT WORK;