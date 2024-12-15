import pandas as pd
import random
from faker import Faker

data = pd.read_excel('test.xlsx')


fake = Faker("ru_RU")

data['Имя'] = [fake.name() for _ in range(len(data))]
data['Телефон'] = [fake.phone_number() for _ in range(len(data))]
data['Email'] = [fake.email() for _ in range(len(data))]

data = data.drop(data.columns[0], axis=1)

data.to_csv('test_with_name.csv', index=False)

