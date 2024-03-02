import logging
from  .caching.sqlite_query import create_sqlite_table

logger = logging.getLogger(__name__)


def get_value_update_string(table, user, row_cached=None):
    if not table.get('columns'):
        return ""
    
    values_array = []
    for column in table['columns']:
        custom = "custom:"
        indice = column['type'].find(custom)
        value = user[column['type']] if indice == -1 else column['type'][indice + len(custom):].strip()
        if row_cached and row_cached.get(column['name']):
            continue
        values_array.append(f"{column['name']} = '{value}'")
    return ",".join(values_array)

def get_left_join_string(table, relation):
    return f"LEFT JOIN {relation['name']} ON {table['name']}.{relation['parent_relation_id']}={relation['name']}.{relation['relation_id']}"

def get_all_left_joins_and_select_columns(parent_table, table, session_sqlite, left_joins=[], select_columns=None, select_ids=None):

    for relation in table.get('relations_tables', []):
        create_sqlite_table(parent_table['caching'], relation, session_sqlite)
        logger.info(f"Anonymizing relation {relation['name']}...")
        select_columns.append(f"{relation['name']}.{relation['id']} as {relation['name']}_{relation['id']}")
        select_ids.append({'name': relation['name'],'id': relation['id']})
        left_joins.append(get_left_join_string(table, relation))

        left_joins, select_columns = get_all_left_joins_and_select_columns(parent_table, relation, session_sqlite, left_joins, select_columns, select_ids)

    return left_joins, select_columns

def get_all_left_joins_and_select_columns_string(table, session_sqlite, left_joins=[]):
    select_columns = [f"{table['name']}.{table['id']} as {table['name']}_{table['id']}"]
    create_sqlite_table(table['caching'], table, session_sqlite)
    select_ids = [{'name': table['name'],'id': table['id']}]

    left_joins, select_columns = get_all_left_joins_and_select_columns(table, table, session_sqlite, left_joins, select_columns, select_ids)
    left_joins_str = " ".join(left_joins)
    select_columns_str = ",".join(select_columns)
    return left_joins_str, select_columns_str, select_ids

def construct_paginated_sql_filter(select_ids, last_row):
    conditions = []

    for i in range(len(select_ids), 0, -1):
        condition_parts = []
        is_null = False
        for j in range(i):
            table_info = select_ids[j]
            table_name = table_info['name']
            column_id = table_info['id']
            value = last_row.get(f"{table_name}_{column_id}")
            is_last = j == i - 1

            if value is None:
                if is_last:
                    is_null = True
                    break
                else:
                    condition_parts.append(f"({table_name}.{column_id} IS NULL OR {table_name}.{column_id} > 0)")
            else:
                operator = ">" if is_last else ">="
                condition_parts.append(f"({table_name}.{column_id} {operator} {value})")

        if not is_null:
            conditions.append(f"( {' AND '.join(condition_parts)} )")

    separator = " OR "
    condition_string = f"({separator.join(conditions)})"

    return condition_string

def where_condition_select_rows(table, select_ids, last_row=None):
    conditions_or = []
    conditions_and = []

    if 'unique' in table.get('target_id', {}):
        unique_values = ', '.join(map(str, table['target_id']['unique']))
        conditions_or.append(f"{table['name']}.{table['id']} IN ({unique_values})")

    if 'range' in table.get('target_id', {}):
        for start, end in table['target_id']['range']:
            conditions_or.append(f"({table['name']}.{table['id']} BETWEEN {start} AND {end})")

    if last_row is not None:
        conditions_and.append(construct_paginated_sql_filter(select_ids, last_row))

    where_clause = ""
    if conditions_or:
        where_clause += " OR ".join(conditions_or)
    if conditions_and:
        and_clause = " AND ".join(conditions_and)
        where_clause = f"({where_clause}) AND {and_clause}" if where_clause else and_clause

    return f"WHERE {where_clause}" if where_clause else ""




