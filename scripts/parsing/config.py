from ..user_generator.user_generator import config_type

common_table_scope = {
    "name": {
        "default_value": None,
        "type": "string",
        "func_check": None,
        "options": None,
    },
    "id": {
        "default_value": None,
        "type": "string",
        "func_check": None,
        "options": None,
    },
    "columns": {
        "default_value": None,
        "type": "object",
        "func_check": None, # valid_column_format() will be loaded.
        "options": None,
    },
    "relations_tables": {
        "default_value": None,
        "type": "object",
        "func_check": None, # valid_relations_table_format() will be loaded.
        "options": None,
    },
}

table_scope = {
    "expected_keys": {"name", "columns"},
    "optional_keys": {"target_id", "id", "relations_tables", "caching"},
    "key_properties": {
        "caching": {
            "default_value": "cache",
            "type": "string",
            "func_check": None,
            "options": ['reset', 'cache', 'no-cache', 'force-cache'],
        },
        "target_id": {
            "default_value": None,
            "type": "string",
            "func_check": None,
            "options": None,
        },
    }
}

relations_table_scope = {
    "expected_keys": {'name'},
    "optional_keys": {'columns', 'relations_tables', 'physics', 'type', 'id', 'relation_id', 'parent_relation_id'},
    "key_properties": {
        "physics": {
            "default_value": "true",
            "type": "string",
            "func_check": None,
            "options": ["true", "false"],
        },
        "type": {
            "default_value": "one_to_many",
            "type": "string",
            "func_check": None,
            "options": ['one_to_one', 'one_to_many'],
        },
        "relation_id": {
            "default_value": None,
            "type": "string",
            "func_check": None,
            "options": None,
        },
        "parent_relation_id": {
            "default_value": None,
            "type": "string",
            "func_check": None,
            "options": None,
        },
    }
}

column_scope = {
    "expected_keys": {"name", "type"},
    "optional_keys": None,
    "key_properties": {
        "name": {
            "default_value": None,
            "type": "string",
            "func_check": None,
            "options": None,
        },
        "type": {
            "default_value": None,
            "type": "string",
            "func_check": None,
            "options": list(config_type.keys()),
        },
    }
}