from sqlalchemy import inspect, MetaData, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.types import Integer, SmallInteger, BigInteger, Float, String, DateTime, Date, Boolean, Numeric, Text,TIMESTAMP, LargeBinary
from datetime import datetime
import logging
from sqlalchemy.sql.schema import ForeignKeyConstraint
from ..user_generator.config import config_type

logger = logging.getLogger(__name__)

def check_table_exists(insp, table_name):
    if not table_name:
        logger.error("No table name provided.")
        return False

    try:
        if insp.has_table(table_name):
            # logger.info(f"Table {table_name} exists.")
            return True
        else:
            logger.error(f"Table {table_name} does not exist.")
            return False
    except Exception as e:
        logger.error(f"Error checking if table {table_name} exists: {e}")
        return False


def convert_to_smallint(value):
        int_value = int(value)
        if -32768 <= int_value <= 32767:
            return int_value
        else:
            raise ValueError(f"Value {value} is out of SmallInteger range.")
        
def convert_to_bigint(value):
    int_value = int(value)
    if -9223372036854775808 <= int_value <= 9223372036854775807:
        return int_value
    else:
        raise ValueError(f"Value {value} is out of BigInteger range.")

def contains_any_of(substrings, target_string):
    return any(substring in target_string for substring in substrings)

type_conversion_map = {
    Integer: lambda value: int(value),
    SmallInteger: convert_to_smallint,
    BigInteger: convert_to_bigint,
    Float: lambda value: float(value),
    Numeric: lambda value: float(value), 
    String: lambda value: value,
    DateTime: lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M:%S"),
    Date: lambda value: datetime.strptime(value, "%Y-%m-%d").date(),
    Boolean: lambda value: value.lower() in ['true', '1', 't', 'y', 'yes']
}

def map_string_to_type(type_string):
    mapping = {
        'integer': (Integer, SmallInteger),
        'string': (String, Text),
        'boolean': (Boolean, TINYINT),
        'date': (Date,),
        'datetime': (DateTime, TIMESTAMP),
        'float': (Float,),
        'largebinary': (LargeBinary,)
    }
    return mapping.get(type_string.lower())

def map_column_type_to_sqlalchemy(column_type_string):
    column_type_string = str(column_type_string).upper().strip()
    
    if "INT" in column_type_string:
        if contains_any_of(["TINY", "SMALL"], column_type_string):
            return SmallInteger
        elif contains_any_of(["BIG", "LONG"], column_type_string):
            return BigInteger
        else:
            return Integer
    elif contains_any_of(["CHAR", "TEXT"], column_type_string):
        return String
    elif contains_any_of(["FLOAT", "DOUBLE"], column_type_string):
        return Float
    elif contains_any_of(["NUMERIC", "DECIMAL"], column_type_string):
        return Numeric
    elif "DATE" in column_type_string:
        if "TIME" in column_type_string:
            return DateTime
        else:
            return Date
    elif "BOOL" in column_type_string:
        return Boolean
    else:
        logger.error(f"Column type {column_type_string} is not supported.")
        return None

def try_convert(value, column_type):
    converter = type_conversion_map.get(map_column_type_to_sqlalchemy(column_type))
    if converter is None:
        logger.error(f"No conversion available for type {column_type}")
        return False
    try:
        converter(value)
        return True
    except ValueError:
        logger.error(f"Value {value} cannot be converted to type {column_type}.")
    return False
    
def check_custom_type(custom_type, type):
    if not custom_type:
        return True
    custom_path = "custom:"
    index = custom_type.find(custom_path)
    

    custom_str = custom_type[index + len(custom_path):].strip()

    return try_convert(custom_str, type)

def check_column_exists_and_type(insp, table_name, column_name, valid_types = None, custom_type = None):
    valid_sqlalchemy_types = tuple(t for type_str in valid_types for t in map_string_to_type(type_str)) if valid_types else None
    if not table_name or not column_name :
        logger.error("Invalid input provided.")
        return False

    try:
        cols = insp.get_columns(table_name)

        col = None
        for c in cols:
            if c['name'] == column_name:
                col = c
                break

        if col is not None:
            if (not valid_types or any(isinstance(col['type'], t) for t in valid_sqlalchemy_types)) and check_custom_type(custom_type, col['type']):
                # logger.info(f"Column {column_name} in table {table_name} is of an acceptable type: {col['type']}.")
                return True
            else:
                logger.error(f"Column {column_name} in table {table_name} is of an unacceptable type: {col['type']}.")
                return False
        else:
            logger.error(f"Column {column_name} does not exist in table {table_name}.")
            return False
    except NoSuchTableError:
        logger.error(f"Table {table_name} does not exist.")
        return False
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return False



def check_all_columns_exist_and_type(engine, table_name, columns, check_if_column_exists=True):
    if check_if_column_exists and not columns:
        logger.error("No columns provided in the table {table_name}.")
        return False
    for column in columns:
        column_name = column['name']
        column_type = column['type']
        is_not_custom = config_type.get(column_type)
        type_allowed = config_type.get(column_type).get('type_allowed') if is_not_custom else []
        custom_type = None if is_not_custom else column_type

        if not check_column_exists_and_type(engine, table_name, column_name, type_allowed, custom_type):
            return False
    return True

def is_relation_table_exists(relations_ids_array, relation_id, parent_relation_id, physics=None):
    if physics == 'false':
        return True
    for relation in relations_ids_array:
        if relation['relation_id'] == relation_id and relation['parent_relation_id'] == parent_relation_id:
            return True
    return False

def is_column_primary_autoincremental(primary_key_column_array, column_name, autoincremental_id=None):
    if autoincremental_id == 'false':
        return True
    for column in primary_key_column_array:
        if column['id'] == column_name:
            return True
    return False


def find_incremental_primary_keys(insp, table_name):
    columns = insp.get_columns(table_name)
    pk_constraint = insp.get_pk_constraint(table_name)
    primary_key_column_array = []
    if pk_constraint and len(pk_constraint['constrained_columns']) == 1:
        primary_key_column_name = pk_constraint['constrained_columns'][0]
        for column in columns:
            if column['name'] == primary_key_column_name:
                if column['autoincrement']:
                    primary_key_column_array.append({'id': primary_key_column_name, 'column_type': column['type']})
    return primary_key_column_array


def find_relations_ids(engine, table_name, parent_table_name):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table_1 = metadata.tables[table_name]
    table_2 = metadata.tables[parent_table_name]

    relations_ids = []
    for constraint in table_1.constraints.union(table_2.constraints):
        if isinstance(constraint, ForeignKeyConstraint):
            for (fk, pk) in zip(constraint.elements, constraint.referred_table.primary_key):
                if fk.parent.table == table_1 and pk.table == table_2:
                    relations_ids.append({'relation_id': fk.parent.name, 'parent_relation_id': pk.name})
                elif fk.parent.table == table_2 and pk.table == table_1:
                    relations_ids.append({'relation_id': pk.name, 'parent_relation_id': fk.parent.name})

    return relations_ids

def check_relation_table(engine, tables, parent_table_name):
    try:
        for relation in tables:
            relation_table_name = relation['name']
            # relation['type'] = relation.get('type', relations_table_scope['key_properties]['type']['default_value'])

            insp = inspect(engine)
            if not check_table_exists(insp, relation_table_name):
                return False

            if not check_and_set_primary_key_column(insp, relation_table_name, relation):
                return False

            relaction_ids = find_relations_ids(engine, relation_table_name, parent_table_name)
            if not relaction_ids and relation.get('physics') == 'true':
                logger.error(f"Table {relation_table_name} does not have a foreign key relation with table {parent_table_name}. 1")
                return False
            relaction_id = relation.get('relation_id', relaction_ids[0].get('relation_id') if len(relaction_ids) == 1 else None)
            parent_relation_id = relation.get('parent_relation_id', relaction_ids[0].get('parent_relation_id') if len(relaction_ids) == 1 else None)
            if relaction_id is None or parent_relation_id is None:
                logger.error(f"Table {relation_table_name} does not have a foreign key relation with table {parent_table_name}. 2")
                return False
            if not check_column_exists_and_type(insp, relation_table_name, relaction_id):
                return False
            if not check_column_exists_and_type(insp, parent_table_name, parent_relation_id):
                return False
            if not is_relation_table_exists(relaction_ids, relaction_id, parent_relation_id, relation.get('physics')):
                logger.error(f"Table {relation_table_name} does not have a foreign key relation with table {parent_table_name}. 3")
                return False

            if not check_all_columns_exist_and_type(insp, relation_table_name, relation.get('columns', []), False):
                return False
            relation['relation_id'] = relaction_id
            relation['parent_relation_id'] = parent_relation_id
            if 'relations_tables' in relation:
                if not check_relation_table(engine, relation['relations_tables'], relation_table_name):
                    return False

        return True
    except Exception as e:
        logger.error(f"Error in relation table {relation_table_name}: {e}")
        return False

def check_and_set_primary_key_column(insp, table_name, table):

    table_incremental_primary_keys = find_incremental_primary_keys(insp, table_name)

    if not table_incremental_primary_keys:
        logger.error(f"Table {table_name} does not have a single autoincremental primary key.")
        return False

    table_id = table.get('id', table_incremental_primary_keys[0].get('id') if len(table_incremental_primary_keys) == 1 else None)

    if table_id is None:
        logger.error(f"Table {table_name} does not have a single autoincremental primary key.")
        return False
    if not check_column_exists_and_type(insp, table_name, table_id):
        return False
    if not is_column_primary_autoincremental(table_incremental_primary_keys, table_id, table.get('autoincremental_id')):
        logger.error(f"Column {table_id} in table {table_name} is not a primary key or part of a unique constraint.")
        return False

    table['id'] = table_id
    return True

def db_error_handling(engine, target_data):
    try:
        for table in target_data['tables']:
            table_name = table['name']
            # table['caching'] = table.get('caching')

            insp = inspect(engine)

            if not check_table_exists(insp, table_name):
                exit(1)
            if not check_and_set_primary_key_column(insp, table_name, table):
                exit(1)
            if not check_all_columns_exist_and_type(insp, table_name, table.get('columns', [])):
                exit(1)
            if 'relations_tables' in table:
                if not check_relation_table(engine, table['relations_tables'], table_name):
                    logger.error(f"Error in relation table {table_name}.")
                    exit(1)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)