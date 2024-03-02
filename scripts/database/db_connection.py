
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DBAPIError, SQLAlchemyError
import logging
from ..utils.utils import hmac_hash_name
import os


logger = logging.getLogger(__name__)

DB_DIALECTS = {
    'postgresql': 'postgresql',
    'mysql': 'mysql+pymysql',
}

REQUIRED_ENV_VARS = ['DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST', 'DATABASE_PORT', 'DATABASE_DB']

DEFAULT_SQLITE_DIR = 'processed_data'

def create_db_url(db_type, user, password, host, port, db_name):
    dialect = DB_DIALECTS.get(db_type)
    if not dialect:
        logger.error(f"Unsupported database type: {db_type}")
        exit(1)
    logger.info(f"Creating database URL for {dialect}...")
    return f"{dialect}://{user}:{password}@{host}:{port}/{db_name}"

def get_engine(db_user, db_password, db_host, db_port, db_name, db_type = 'postgresql'):
    try:
        db_url = create_db_url(db_type, db_user, db_password, db_host, db_port, db_name)
        engine = create_engine(db_url)
        engine.connect()
        logger.info("Successfully connected to the database.")
        return engine
    except OperationalError:
        logger.error("Operational Error: Unable to connect to the database. Check the connection string.")
    except DBAPIError:
        logger.error("DBAPI Error: Problem in database communication.")
    except SQLAlchemyError:
        logger.error("SQLAlchemy Error: Issue in handling the database connection.")
    except Exception as e:
        logger.exception("Generic Error: An unexpected error occurred.")
    return None

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

def get_engine_and_session(db_user, db_password, db_host, db_port, db_name, db_type = 'postgresql'):
    engine = get_engine(db_user, db_password, db_host, db_port, db_name, db_type)
    if engine is None:
        return None, None
    return engine, get_session(engine)

def check_env_vars_db():
    if not all(os.getenv(env_var) for env_var in REQUIRED_ENV_VARS):
        logger.error("All required environment variables are not set. Please check your environment variables and try again.")
        exit(1)

def init_db_connection():
    db_user = os.getenv('DATABASE_USER')
    db_name = os.getenv('DATABASE_DB')
    db_host = os.getenv('DATABASE_HOST')
    db_port = os.getenv('DATABASE_PORT')
    db_password = os.getenv('DATABASE_PASSWORD')
    db_type = os.getenv('DATABASE_TYPE', 'postgresql')
    try:
        engine, session = get_engine_and_session(db_user, db_password, db_host, db_port, db_name, db_type)
        if engine is None or session is None:
            logger.error("Failed to establish a database connection.")
            exit(1)
    except Exception as e:
        logger.error(f"Failed to establish a database connection: {e}")
        exit(1)

    
    return engine, session

def sqlite_db_connection(db_name):
    try:
        logger.info(f"Creating database URL for sqlite... {db_name}")
        engine = create_engine(f'sqlite:///{DEFAULT_SQLITE_DIR}/{db_name}')
        engine.connect()
        logger.info("Successfully connected to the database.")
        return get_session(engine)
    except OperationalError:
        logger.error("Operational Error: Unable to connect to the database. Check the connection string.")
    except DBAPIError:
        logger.error("DBAPI Error: Problem in database communication.")
    except SQLAlchemyError:
        logger.error("SQLAlchemy Error: Issue in handling the database connection.")
    except Exception as e:
        logger.exception("Generic Error: An unexpected error occurred.")
    return None

def init_sqlite_db_connection():
    try:
        if not os.path.exists(DEFAULT_SQLITE_DIR):
            os.makedirs(DEFAULT_SQLITE_DIR)
            
        db_name = f"{os.getenv('DATABASE_HOST')}-{os.getenv('DATABASE_PORT')}-{os.getenv('DATABASE_DB')}-{os.getenv('DATABASE_USER')}"
        db_name = hmac_hash_name(db_name, os.getenv('SECRET_KEY', 'not_so_secret_key'))
        session_sqlite = sqlite_db_connection(db_name)
        if session_sqlite is None:
            logger.error("Failed to establish a database sqlite connection.")
            exit(1)
        return session_sqlite
    except Exception as e:
        logger.error(f"Failed to establish a database sqlite connection: {e}")
        exit(1)