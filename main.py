# main.py
from scripts.database.db_connection import check_env_vars_db, init_db_connection, init_sqlite_db_connection
from scripts.database.db_error_handling import db_error_handling
from scripts.database.anonymise import anonymize_all_tables
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging
import yaml
import json
import argparse
from scripts.parsing.parser import parser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(file_path):
    try:
        with open(file_path, 'r') as f:
            if file_path.endswith('.json'):
                return parser(json.load(f))
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                return parser(yaml.safe_load(f))
            else:
                raise ValueError("Unsupported file format. Please use .json or .yaml/.yml files.")
    except Exception as e:
        raise ValueError(f"Error loading config file: {e}")

def parse_arguments():
    arg_parser = argparse.ArgumentParser(description="Enter your configuration file for sensitive data")
    arg_parser.add_argument('config_file', type=str, help='Path to the .yaml or .json configuration file')
    return arg_parser.parse_args()

def anonymisation(session, target_data, session_sqlite):
    try:
        anonymize_all_tables(session, target_data['tables'], session_sqlite)
        # session.commit()
        # session_sqlite.commit()
        logger.info("Database operations executed and committed successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        session_sqlite.rollback()
        logger.error(f"An error occurred during database operations: {e}")
    finally:
        session_sqlite.close()
        session.close()
if __name__ == "__main__":
    try:
        args = parse_arguments()
        target_data = load_config(args.config_file)

        logger.info(f"target_data after parsing:\n{json.dumps(target_data, indent=4)}")

        load_dotenv()
        check_env_vars_db()
        engine, session = init_db_connection()
        db_error_handling(engine, target_data)

        logger.info(f"target_data after db_error_handling:\n{json.dumps(target_data, indent=4)}")


        
        session_sqlite = init_sqlite_db_connection()

        anonymisation(session, target_data, session_sqlite)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
