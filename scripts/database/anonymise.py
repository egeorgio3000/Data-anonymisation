from sqlalchemy import text
from ..user_generator.user_generator import create_random_user_sample
from tqdm import tqdm
import logging
from .query.create_query import get_all_left_joins_and_select_columns_string, where_condition_select_rows
from .query.commit_query import update_query, commit_changes
from .query.relations import anonymize_relations
from ..utils.utils import get_env_var
import time

logger = logging.getLogger(__name__)


def anonymize_loop(session, session_sqlite, table, query_dict, select_ids, result_count=0):

    if result_count != 0 and result_count < query_dict['limit_select']:
        return
    query = f"SELECT {query_dict['select_columns']}\n" \
                f"FROM {table['name']}\n" \
                f"{query_dict['left_joins']}\n" \
                f"{query_dict['where_condition']}\n" \
                f"ORDER BY {query_dict['order_by']}\n" \
                f"LIMIT {query_dict['limit_select']}"

    logger.info(f"Query\n---------------------------------\n{query}\n---------------------------------")

    time.sleep(get_env_var('TIME_QUERY_SELECT', default=0.2, cast_type=float))
    result = session.execute(text(query))
    new_result_count = result.rowcount

    if new_result_count == 0:
        return

    last_row = None
    logger.info(f"Anonymizing {new_result_count} rows...")
    for row in tqdm(result, total=new_result_count):
        row = row._asdict()
        user = create_random_user_sample()
        update_query(session, session_sqlite, table, table, row, user, False, 'id', table['id'])
        anonymize_relations(session, session_sqlite, table, table, user, row)
        last_row = row

        # logger.info(f"row -- {row}\---------------------------------")

    if last_row:
        query_dict['where_condition'] = where_condition_select_rows(table, select_ids, last_row)
        anonymize_loop(session, session_sqlite, table, query_dict, select_ids, new_result_count)



def anonymize_table(session, table, session_sqlite):
    logger.info(f"Anonymizing table {table['name']}...")
    limit_select = get_env_var('LIMIT_QUERY_SELECT', default=1000, cast_type=int)

    left_joins, select_columns, select_ids = get_all_left_joins_and_select_columns_string(table, session_sqlite)

    where_condition = where_condition_select_rows(table, select_ids)

    order_by = ",".join([f"{table['name']}.{table['id']}" for table in select_ids])

    query_dict = {
        'left_joins': left_joins,
        'select_columns': select_columns,
        'order_by': order_by,
        'where_condition': where_condition,
        'limit_select': limit_select
    }
    anonymize_loop(session, session_sqlite, table, query_dict, select_ids)
    commit_changes(session, session_sqlite, table, True)


def anonymize_all_tables(session, entry: [object], session_sqlite):
    logger.info(f"{len(entry)} tables")
    for table in entry:
        table['count_commit'] = 0
        table['processed_data'] = {}
        anonymize_table(session, table, session_sqlite)
        table = {} 