from sqlalchemy import text
import logging

def execute_sqlite_query(session_sqlite, query, commit=True):
    try:
        session_sqlite.execute(text(query))
        if commit:
         session_sqlite.commit()
    except Exception as e:
        logging.error(f"Error executing query in sqlite: {e}")
        raise e

def get_column_names(session_sqlite, table_name):
    query = f"PRAGMA table_info({table_name});"
    result = session_sqlite.execute(text(query))
    columns = []
    for row in result.fetchall():
        row = row._asdict()
        columns.append(row['name'])
    return columns

def create_sqlite_table(caching_options, table, session_sqlite):
    try:
        if caching_options == "no-cache":
            return
        if caching_options == "reset":
            execute_sqlite_query(session_sqlite, f"DROP TABLE IF EXISTS {table['name']}", commit=False) 
        execute_sqlite_query(session_sqlite, f"CREATE TABLE IF NOT EXISTS {table['name']} ({table['id']} INTEGER PRIMARY KEY)", commit=False)
        columns_already_created = get_column_names(session_sqlite, table['name'])
        for column in table.get('columns', []):
            if column['name'] in columns_already_created:
                continue
            execute_sqlite_query(session_sqlite, f"ALTER TABLE {table['name']} ADD COLUMN {column['name']} BOOLEAN DEFAULT FALSE", commit=False)
    except Exception as e:
        logging.error(f"Error creating table {table['name']} in sqlite: {e}")
        exit(1)


def is_row_exists(session_sqlite, table_name, column_name, value):
    try:
        query = f"SELECT * FROM {table_name} WHERE {column_name} = :value"
        result = session_sqlite.execute(text(query), {'value': value}).fetchone()
        return result
    except Exception as e:
        logging.error(f"Error checking if row exists in {table_name} in sqlite: {e}")
        exit(1)

def add_row_to_sqlite_table(session_sqlite, table_name, column_names, values):
    try:
        column_name = ",".join(column_names)
        value = ",".join([f"'{value}'" for value in values])
        value_update_string = ",".join([f"{column} = '{value}'" for column, value in zip(column_names, values)])
        query = f"INSERT INTO {table_name} ({column_name}) VALUES ({value}) ON CONFLICT DO UPDATE SET {value_update_string}"
        execute_sqlite_query(session_sqlite, query, commit=False)
    except Exception as e:
        logging.error(f"Error adding row to {table_name} in sqlite: {e}")
        exit(1)