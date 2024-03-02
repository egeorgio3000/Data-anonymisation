import re
from . import config
from ..utils import utils_parser

def valid_format(data):

    if set(data.keys()) != {"tables"}:
        raise ValueError("Main keys should be 'tables'.")

    duplicate_tables = set()

    for i, table in enumerate(data["tables"]):
        # Expected / Optional keys
        if not set(table.keys()).issuperset(config.table_scope["expected_keys"]):
            raise ValueError(f"Table at index {i} does not have the required keys {config.table_scope['expected_keys']}.")
        if not set(table.keys()).issubset(config.table_scope["expected_keys"] | config.table_scope["optional_keys"]):
            raise ValueError(f"Table {table['name']} at index {i} has unexpected keys.")

        # Fullfil default value data
        diff = config.table_scope["optional_keys"] - table.keys()

        for key in diff:
            default_value = config.table_scope["key_properties"][key]["default_value"]
            if default_value:
                table[key] = default_value

        # Duplicata for table names
        if table["name"] in duplicate_tables:
            raise ValueError(f"Duplicate Table {table['name']} found at index {i}.")

        # Parsing key properties
        for key, value in table.items():
            
            # Checking type with isinstance(), create a larger selection afterwards
            t = str if config.table_scope["key_properties"][key]["type"] == 'string' else object
            if not isinstance(table[key], t) or not table[key]:
                raise ValueError(f"Value for key '{key}' at table '{table['name']}' at index {i} is not a {config.table_scope['key_properties'][key]['type']} or field is empty.")
            
            # Checking options and their validity
            if config.table_scope["key_properties"][key]["options"]:
                if value not in config.table_scope["key_properties"][key]["options"]:
                    raise ValueError(f"Value for key '{key}' at table '{table['name']}' at index {i} is not a valid option {config.table_scope['key_properties'][key]['options']}.")
            
            # Checking functions, and launching adequate function accordingly
            if config.table_scope["key_properties"][key]["func_check"]:
                func = config.table_scope["key_properties"][key]["func_check"]
                func(table[key], table["name"], i)

        duplicate_tables.add(table["name"])
    return True

def seq_wrap(unique_ids, range_pair_ids):
    if unique_ids:
        sorted_set = sorted(unique_ids)
        new_range_pair_ids = []
        start = end = sorted_set[0]
        
        for n in sorted_set[1:]:
            if n == end + 1:
                end = n
            else:
                if start != end:
                    new_range_pair_ids.append((start, end))
                start = end = n
        if start != end:
            new_range_pair_ids.append((start, end))
        range_pair_ids.extend(new_range_pair_ids)
        
        for plage in range_pair_ids:
            start, end = plage
            unique_ids.difference_update(set(range(start, end + 1)))
    return [list(unique_ids), range_pair_ids]

def extract_target_ids(target_id):
    range_pair_ids = []
    unique_ids = set()
    id_values = target_id.replace(' ', '').split(',')
    
    for id_val in id_values:
        if ':' in id_val:
            range_format = re.compile(r'^(\d+):(\d+)$')
            valid_format = range_format.match(id_val)
            if valid_format:
                n1 = (int(valid_format.group(1)))
                n2 = (int(valid_format.group(2)))
                if n1 > n2:
                    raise ValueError(f"The range order for target_id is invalid. Please use the following order: ['1:100'].")
            else:
                raise ValueError(f"The range format for target_id is invalid. Please use the following example: ['1:100'].")
            range_pair = (n1, n2)
            range_pair_ids.append(range_pair)
        else:
            unique_ids.add(int(id_val))
    return seq_wrap(unique_ids, range_pair_ids)

def update_scope_properties():
    # Init functions
    config.common_table_scope["columns"]["func_check"] = utils_parser.valid_column_format
    config.common_table_scope["relations_tables"]["func_check"] = utils_parser.valid_relations_table_format

    # Extend common data in different scopes
    config.table_scope["key_properties"].update(config.common_table_scope)
    config.relations_table_scope["key_properties"].update(config.common_table_scope)

def parser(data):
    update_scope_properties()

    if not valid_format(data):
        raise ValueError(f"Syntax parsing error: Unable to interpret the source code.")
    
    # print(data["tables"][0]["relations_tables"])

    for table in data["tables"]:
        table_name = table["name"]
        target_id = table.get("target_id", "")
        if target_id:
            target_ids = extract_target_ids(target_id)
            table["target_id"] = {}
            if target_ids[0]:
                table["target_id"]["unique"] = target_ids[0]
            if target_ids[1]:
                table["target_id"]["range"] = target_ids[1]
    return data