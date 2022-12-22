import pandas as pd
from pandas import isnull, notnull
from datetime import datetime
import json

format_month = lambda month: str(month) if month >= 10 else f'0{month}'

with open('currency_by_years.json', 'r') as file:
    cur_multipliers = json.load(file)

data: pd.DataFrame = pd.read_csv('vacancies_dif_currencies.csv')[:100]

salary_values = []

columns = ('salary_from', 'salary_to', 'salary_currency', 'published_at')

for index, (salary_from, salary_to, salary_currency, published_at) in enumerate(zip(*[data[c] for c in columns])):
    if isnull(salary_from) and isnull(salary_to):
        data = data.drop(index=index)
        continue

    salary = 0

    if notnull(salary_from) and notnull(salary_to):
        salary = (salary_from + salary_to) / 2
    elif notnull(salary_from) and isnull(salary_to):
        salary = salary_from
    elif isnull(salary_from) and notnull(salary_to):
        salary = salary_to

    published_at = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S+%f')
    date_key = f'{published_at.year}-{format_month(published_at.month)}'

    if notnull(salary_currency) and salary_currency != 'RUR':
        if salary_currency not in cur_multipliers[date_key].keys():
            data = data.drop(index=index)
            continue
        if not cur_multipliers[date_key][salary_currency]:
            data = data.drop(index=index)
            continue
        
        salary *= cur_multipliers[date_key][salary_currency]

    salary_values.append(salary)

    if len(salary_values) == 100:
        break

data.insert(2, 'salary', salary_values)
for column in ('salary_from', 'salary_to', 'salary_currency'):
    del data[column]

data.to_csv('result.csv', index=False)
