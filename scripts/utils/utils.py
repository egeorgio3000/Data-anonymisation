import os
import hashlib
import hmac

def get_env_var(var_name, default, cast_type):
    value = os.getenv(var_name)
    if value is not None:
        try:
            return cast_type(value)
        except ValueError:
            pass
    return default

def hmac_hash_name(name, key):
    key_bytes = key.encode()
    name_bytes = name.encode()
    
    hmac_object = hmac.new(key_bytes, name_bytes, hashlib.sha256)
    
    hash_hex = hmac_object.hexdigest()
    
    return hash_hex