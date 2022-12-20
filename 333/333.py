import requests
import json
import time
import pandas as pd

def get_page(page):
    params = {
        'specialization': 1,
        'page': page,
        'per_page': 100,
        'period': 1
    }   
    req = requests.get('https://api.hh.ru/vacancies', params)
    data = req.content.decode()
    req.close()

    return data

result = []

for page in range(20):

    try:
        req = json.loads(get_page(page))
    except Exception as e:
        raise e

    for vacancy_data in req['items']:
        vacancy = {k: None for k in ('name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at')}
        vacancy['name'] = vacancy_data['name']
        vacancy['area_name'] = vacancy_data['area']['name']
        vacancy['published_at'] = vacancy_data['published_at']

        if vacancy_data['salary']:
            vacancy['salary_from'] = vacancy_data['salary']['from']
            vacancy['salary_to'] = vacancy_data['salary']['to']
            vacancy['salary_currency'] = vacancy_data['salary']['currency']
        
        result.append(vacancy)

    time.sleep(0.25)
        
pd.DataFrame.from_records(result).to_csv('desktop/result.csv')
