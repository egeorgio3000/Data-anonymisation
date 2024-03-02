
from .config import config_type, supplementary_args_default
import logging

logger = logging.getLogger(__name__)

def generate_anonymized_user_data(config, supplementary_args={}):

    anonymized_data = {}

    for key, field_config in config.items():
        if "function" in field_config:
            function_config = field_config["function"]
            function = function_config["name"]
            
            internal_derived_args_names = function_config["args"].get("internal_derived", [])
            supplementary_args_names = function_config["args"].get("supplementary", [])

            internal_derived_args = [anonymized_data[arg] for arg in internal_derived_args_names if arg in anonymized_data]
            supplementary_args_values = [supplementary_args[arg] for arg in supplementary_args_names if arg in supplementary_args]

            final_args = internal_derived_args + supplementary_args_values
            anonymized_data[key] = function(*final_args)

    return anonymized_data

def create_random_user_sample(supplementary_args={}):
    for key, value in supplementary_args_default.items():
        if key not in supplementary_args:
            supplementary_args[key] = value

    random_user = generate_anonymized_user_data(config_type, supplementary_args)
    # logger.info(f"Random user: {random_user}")
    return random_user