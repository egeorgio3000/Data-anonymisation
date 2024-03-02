from .commit_query import update_query

def one_to_one_relation(session, session_sqlite, table, relation, user, row):
    # update_query(session, session_sqlite, table, relation, row, user, False, 'relation_id', table['id'])
    update_query(session, session_sqlite, table, relation, row, user, False, 'id', relation['id'])

def one_to_many_relation(session, session_sqlite, table, relation, user, row):
    update_query(session, session_sqlite, table, relation, row, user, True, 'id', relation['id'])



def anonymize_relations(session, session_sqlite, parent_table, table, user, row):
    for relation in table.get('relations_tables', []):
        if relation['type'] == "one_to_one":
            one_to_one_relation(session, session_sqlite, parent_table, relation, user, row)
        elif relation['type'] == "one_to_many":
            one_to_many_relation(session, session_sqlite, parent_table, relation, user, row)
        anonymize_relations(session, session_sqlite, parent_table, relation, user, row)