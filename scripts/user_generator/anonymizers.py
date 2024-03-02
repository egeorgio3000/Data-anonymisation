from .faker_utils import fake, Faker
import random
import logging

logger = logging.getLogger(__name__)

def generate_random_civility(civility_mapping):
    if not civility_mapping:
        logger.error("Invalid civility mapping")
        exit(1)
    return  random.choice(list(civility_mapping.values()))


def generate_fake_firstname(civility, civility_mapping):
    faker_generators = {
        "male": fake.first_name_male(),
        "female": fake.first_name_female(),
        "non-binary": fake.first_name_nonbinary()
    }

    for key, value in civility_mapping.items():
        if civility == value:
            if key in faker_generators:
                return faker_generators[key]

    logger.error("Invalid civility for given mapping")
    exit(1)


def generate_fake_lastname():
    return fake.last_name()

def generate_fake_email(firstname, lastname):
    return f"{firstname.lower()}.{lastname.lower()}@{fake.free_email_domain()}"

def generate_fake_imgurl():
    return fake.image_url()

def generate_fake_address():
    address = fake.address()
    while (not address[:address.find(',')].isnumeric()):
        address = fake.address()
    return address

def generate_fake_address_number(address: str):
    return address[:address.find(',')]

def generate_fake_address_streetname(address: str):
    return address[address.find(','):address.find('\n')][2:]

def generate_fake_address_zipcode(address:str):
    return address[address.find('\n') + 1: address[address.find('\n'):].find(' ') + address.find('\n') + 1]

def generate_fake_address_city(address:str):
    return address[address[address.find('\n'):].find(' ') + address.find('\n') + 1:]

def generate_fake_current_country():
    return fake.current_country()

def generate_fake_iban():
    return fake.iban()

def generate_fake_swift():
    return fake.swift()

def generate_fake_card_number():
    return fake.credit_card_number(card_type="visa")

def generate_fake_card_cvc():
    return fake.credit_card_security_code(card_type="visa")

def generate_fake_card_expiration():
    return "20" + fake.credit_card_expire(date_format="%y-%m") + "-01"

def generate_fake_password():
    return fake.password(length=40, special_chars=False, upper_case=False)