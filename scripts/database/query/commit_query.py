import logging
from sqlalchemy import text
from ...user_generator.user_generator import create_random_user_sample
from .create_query import get_value_update_string
from .caching.cache import check_row_cached, update_cache
from ...utils.utils import get_env_var
import time

logger = logging.getLogger(__name__)

def commit_changes(session, session_sqlite, table, last_commit=False):
    if last_commit is False:
        table['count_commit'] += 1
    count_commit = table['count_commit']

    limit_query_commit = get_env_var('LIMIT_QUERY_COMMIT', default=250, cast_type=int)

    if count_commit >= limit_query_commit or (last_commit is True and count_commit > 0):
        time.sleep(get_env_var('TIME_QUERY_COMMIT', default=0.2, cast_type=float))
        logger.info(f"Commiting {count_commit} changes...")
        session.commit()
        session_sqlite.commit()
        table['count_commit'] = 0

def execute_query_update(session, table, values_update_str, column, value):
    query_update = f"UPDATE {table} SET {values_update_str} WHERE {column}={value}"
    # logger.info(f"Query\n---------------------------------\n{query_update}\n---------------------------------")
    session.execute(text(query_update))


def get_columns_to_update(relation):
    columns = []
    for column in relation.get('columns', []):
        columns.append(column['name'])
    return columns

def update_query(session, session_sqlite, table, relation, row, user=None, use_random_user=False, relation_column_key=None, relation_value_key=None):
    if not relation.get('columns'):
        return
        
    value_id = row.get(f"{relation['name']}_{relation_value_key}")
    column_id = relation.get(relation_column_key)
    if value_id is None or column_id is None:
        return

    columns_to_update = get_columns_to_update(relation)
    is_row_cached, row_cached = check_row_cached(table, relation['name'], session_sqlite, table.get('caching'), column_id, value_id, columns_to_update)

    if not is_row_cached :

        if use_random_user:
            user = create_random_user_sample()

        values_update_str = get_value_update_string(relation, user, row_cached)
        if not values_update_str:
            return
        
        execute_query_update(session, relation['name'], values_update_str, column_id, value_id)
        update_cache(table, relation['name'], session_sqlite, table.get('caching'), column_id, value_id, columns_to_update, row_cached)
        commit_changes(session, session_sqlite, table)