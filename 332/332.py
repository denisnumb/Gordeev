from stats import *
import pandas as pd
import json

format_month = lambda month: str(month) if month >= 10 else f'0{month}'

with open('currency_by_years.json', 'r') as file:
    cur_multipliers = json.load(file)

data: List[Vacancy] = csv_filer(*csv_reader('vacancies_dif_currencies.csv'))

result = []

for vacancy in data:
    if not vacancy.salary.salary_from and not vacancy.salary.salary_to:
        continue

    salary = 0

    if vacancy.salary.salary_from and vacancy.salary.salary_to:
        salary = (float(vacancy.salary.salary_from) + float(vacancy.salary.salary_to)) / 2
    elif vacancy.salary.salary_from and not vacancy.salary.salary_to:
        salary = float(vacancy.salary.salary_from)
    elif not vacancy.salary.salary_from and vacancy.salary.salary_to:
        salary = float(vacancy.salary.salary_to)

    cur = vacancy.salary.salary_currency
    date_key = f'{vacancy.published_at.year}-{format_month(vacancy.published_at.month)}'

    if cur and cur != 'RUR':
        if cur not in cur_multipliers[date_key].keys():
            continue
        if not cur_multipliers[date_key][cur]:
            continue
        
        salary *= cur_multipliers[date_key][cur]

    result.append({'name': vacancy.name, 'salary': salary, 'area_name': vacancy.area_name, 'published_at': str(vacancy.published_at)})

    if len(result) == 100:
        break

pd.DataFrame.from_records(result).to_csv('result.csv')
