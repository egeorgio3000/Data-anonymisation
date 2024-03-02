
from .anonymizers import *
config_type = {
    "civility": {
        "type_allowed": ["string", "boolean", "integer"],
        "function": {
            "name": generate_random_civility,
            "args": {
                "internal_derived": [],
                "supplementary": ["civility_mapping"]
            }
        }
    },
    "firstname": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_firstname,
            "args": {
                "internal_derived": ["civility"],
                "supplementary": ["civility_mapping"]
            
            }
        }
    },
    "lastname": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_lastname,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
    "email": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_email,
            "args": {
                "internal_derived": ["firstname", "lastname"],
                "supplementary": []
            }
        }
    },
    "imgurl": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_imgurl,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
	"address": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_address,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
    "address_number": {
        "type_allowed": ["integer", "string"],
        "function": {
            "name": generate_fake_address_number,
            "args": {
                "internal_derived": ["address"],
                "supplementary": []
            }
        }
    },
    "address_streetname": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_address_streetname,
            "args": {
                "internal_derived": ["address"],
                "supplementary": []
            }
        }
    },
    "address_zipcode": {
        "type_allowed": ["integer", "string"],
        # todo: string
        "function": {
            "name": generate_fake_address_zipcode,
            "args": {
                "internal_derived": ["address"],
                "supplementary": []
            }
        }
    },
    "address_city": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_address_city,
            "args": {
                "internal_derived": ["address"],
                "supplementary": []
            }
        }
    },
    "current_country": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_current_country,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
    "iban": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_iban,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
    "swift": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_swift,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
    "card_number": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_card_number,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
    "card_cvc": {
        "type_allowed": ["integer", "string"],
        "function": {
            "name": generate_fake_card_cvc,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
    "card_expiration": {
        "type_allowed": ["date"],
        "function": {
            "name": generate_fake_card_expiration,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    },
    "password": {
        "type_allowed": ["string"],
        "function": {
            "name": generate_fake_password,
            "args": {
                "internal_derived": [],
                "supplementary": []
            }
        }
    }
}

supplementary_args_default = {
    "civility_mapping": {
        "male": "M",
        "female": "MME"
    }
}
