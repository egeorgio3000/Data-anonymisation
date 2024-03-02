from faker import Faker
import random


fake = Faker(['fr_FR'])
Faker.seed('Env variable' + str(random.randint(0, 1000)))
