from ..parsing import config

def valid_column_format(columns, table_name, i):
    duplicate_columns = set()
    for j, column in enumerate(columns):
        column_key_set = set(column.keys())
        
        # Expected keys
        if not column_key_set == config.column_scope["expected_keys"]:
            raise ValueError(f"Column at index {j} in table {table_name} at index {i} does not have the expected keys.")

         # Parsing key properties
        for key, value in column.items():

            # Checking type with isinstance(), create a larger selection afterwards
            if column["name"] in duplicate_columns:
                raise ValueError(f"Column '{column['name']}' is duplicated at index {j}.")

            # Checking type with isinstance(), create a larger selection afterwards
            t = str if config.column_scope["key_properties"][key]["type"] == 'string' else object

            if not isinstance(value, t) or not value:
                raise ValueError(f"Value for key '{key}' at column '{column['name']}' at index {j} from table {table_name} at index {i} is not a {config.column_scope['key_properties'][key]['type']} or field is empty.")
            
            # Checking options and their validity
            if config.column_scope["key_properties"][key]["options"]:
                if value not in config.column_scope["key_properties"][key]["options"] and not value.startswith('custom:'):
                    raise ValueError(f"Value for key '{key}' at column '{column['name']}' at index {j} from table {table_name} at index {i} is not a valid option {config.column_scope['key_properties'][key]['options']}.")
            
            # USELESS IN THIS CASE !!! Checking functions, and launching adequate function accordingly
            if config.column_scope["key_properties"][key]["func_check"]:
                func = config.column_scope["key_properties"][key]["func_check"]
                func(value, table_name, i)  
        
        duplicate_columns.add(column["name"])
    return True

def valid_relations_table_format(relation_table, table_name, i):
    for j, relation in enumerate(relation_table):
        
        # Expected / Optional keys
        if not set(relation.keys()).issuperset(config.relations_table_scope["expected_keys"]):
            raise ValueError(f"Relation table from table {table_name} does not have the required keys {config.relations_table_scope['expected_keys']}.")
        if not set(relation.keys()).issubset(config.relations_table_scope["expected_keys"] | config.relations_table_scope["optional_keys"]):
            raise ValueError(f"Relation table from table {table_name} at index {j} has unexpected keys.")

        # Fullfil default value data
        diff = config.relations_table_scope["optional_keys"] - relation.keys()
        
        for key in diff:
            default_value = config.relations_table_scope["key_properties"][key]["default_value"]
            if default_value:
                relation[key] = default_value

        # Parsing key properties
        for key, value in relation.items():
            t = str if config.relations_table_scope["key_properties"][key]["type"] == 'string' else object
            if not isinstance(value, t) or not value:
                raise ValueError(f"Value for key '{key}' at table '{table_name}' at index {i} is not a {config.relations_table_scope['key_properties'][key]['type']} or field is empty.")
            
            # Checking options and their validity
            if config.relations_table_scope["key_properties"][key]["options"]:
                if value not in config.relations_table_scope["key_properties"][key]["options"]:
                    raise ValueError(f"Value for key '{key}' at table '{table_name}' at index {i} is not a valid option {config.relations_table_scope['key_properties'][key]['options']}.")
            
            # Checking functions, and launching adequate function accordingly
            if config.relations_table_scope["key_properties"][key]["func_check"]:
                func = config.relations_table_scope["key_properties"][key]["func_check"]
                func(relation[key], relation["name"], i)

    return True