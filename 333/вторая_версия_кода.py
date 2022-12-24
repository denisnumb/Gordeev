import requests
import json
import time
from random import choice
from datetime import datetime, timedelta

headers = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0',
        'Accept': '*/*'
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
        'Accept': '*/*'
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Debian; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
        'Accept': '*/*'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 3.1; rv:76.0) Gecko/20100101 Firefox/69.0',
        'Accept': '*/*'
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Debian; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/76.0",
        'Accept': '*/*'
    },
]

fields = ('name', 'description', 'key_skills', 'employer', 'salary', 'area_name', 'published_at')
published_at_time: datetime = datetime.strptime('2022-12-05T00:00:00', '%Y-%m-%dT%H:%M:%S')

result = []

def send_request(url: str, params: dict={}) -> dict:
    req: requests.Response = requests.get(url, params, headers=choice(headers))
    data = req.content.decode()
    req.close()

    if req.status_code != 200:
        print(f'Ошибка {req.status_code} при выполнении запроса\n\t↳ {req.url}\n\n{json.loads(data)}\n')
        if input('1 — повторить запрос\n2 — пропустить запрос\n> ') == '1':
            return send_request(url, params)
        else:
            return False

    return json.loads(data)

def get_page(page: int, df: str, dt: str) -> dict:
    params = {
        'specialization': 1,
        'page': page,
        'per_page': 100,
        'date_from': df,
        'date_to': dt
    }   
    
    return send_request('https://api.hh.ru/vacancies', params)

def get_vacancy(vacancy_id: str) -> dict:
    vacancy_data = send_request(f'https://api.hh.ru/vacancies/{vacancy_id}')
    if not vacancy_data:
        return False

    vacancy = {k: None for k in fields}

    vacancy['name'] = vacancy_data['name']
    vacancy['description'] = vacancy_data['description']
    vacancy['key_skills'] = ', '.join(skill['name'] for skill in vacancy_data['key_skills'])
    vacancy['employer'] = vacancy_data['employer']['name'] if vacancy_data['employer'] else '—'
    vacancy['area_name'] = vacancy_data['area']['name']
    vacancy['published_at'] = vacancy_data['published_at']
    
    if vacancy_data['salary']:
        FROM = vacancy_data['salary']['from']
        TO = vacancy_data['salary']['to']

        if FROM and TO:
            vacancy['salary'] = (FROM + TO) // 2
        elif FROM and not TO:
            vacancy['salary'] = FROM
        elif TO and not FROM:
            vacancy['salary'] = TO

        vacancy['salary'] = f'{vacancy["salary"]} {vacancy_data["salary"]["currency"]}'

    return vacancy


for _ in range(24):
    df = published_at_time.strftime('%Y-%m-%dT%H:%M:%S')
    published_at_time += timedelta(hours=1)
    dt = published_at_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    req = get_page(0, df, dt)
    print(f'Получено количество страниц ({req["pages"]}) для промежутка часов: {published_at_time.hour-1}—{published_at_time.hour}')

    for page in range(req['pages']):
        req = get_page(page, df, dt)

        for short_vacancy_data in req['items']:
            vacancy = get_vacancy(short_vacancy_data['id'])
            if vacancy:
                result.append(vacancy)
            
            time.sleep(0.01)
        
        print(f'\t↳ Получен список вакансий со страницы {page}. Количество: {len(req["items"])}')

        time.sleep(0.25)
        
with open('C:\\Users\\denisnumb\\Desktop\\result.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(result, indent=4, ensure_ascii=False))
