
from .sqlite_query import is_row_exists, add_row_to_sqlite_table

def is_caching_options(caching_options):
    return caching_options in ["cache", "reset", 'force-cache']

def is_force_cache(caching_options):
    return caching_options == 'force-cache'

def check_row_cached(table, relation_name, session_sqlite, caching_options, column_id, value_id, columns_to_update):
    row_cached = None
    
    is_cached_in_memory = value_id in table.get('processed_data', {}).get(relation_name, set())

    if is_cached_in_memory:
        return True, row_cached

    if not is_caching_options(caching_options) or is_force_cache(caching_options):
        return False, row_cached

    is_cached = False
    is_cached_in_sqlite = is_row_exists(session_sqlite, relation_name, column_id, value_id)
    
    if is_cached_in_sqlite:
        is_cached = True
        row_cached = is_cached_in_sqlite._asdict()
        for column in columns_to_update:
            if not row_cached.get(column):
                is_cached = False
                break
                
    return is_cached, row_cached
    
def update_cache(table, relation_name, session_sqlite, caching_options, column, value_id, columns_to_update, row_cached = None):

    columns = [column]
    values = [value_id]
    
    if relation_name not in table['processed_data']:
        table['processed_data'][relation_name] = set()
    table['processed_data'][relation_name].add(value_id)

    if not is_caching_options(caching_options):
        return
    
    for column in columns_to_update:
        if not is_force_cache(caching_options) and row_cached and row_cached.get(column):
            continue
        columns.append(column)
        values.append('true')

    add_row_to_sqlite_table(session_sqlite, relation_name, columns, values)