import csv
import re
from typing import List
from datetime import datetime

title_names = {'name': 'Название', 'description': 'Описание', 'key_skills': 'Навыки', 'experience_id': 'Опыт работы', 'premium': 'Премиум-вакансия', 'employer_name': 'Компания', 'salary': 'Оклад', 'salary_from': 'Нижняя граница вилки оклада', 'salary_to': 'Верхняя граница вилки оклада', 'salary_gross': 'Оклад указан до вычета налогов', 'salary_currency': 'Идентификатор валюты оклада', 'area_name': 'Название региона', 'published_at': 'Дата публикации вакансии'}
table_fields = {'name': 'Название', 'description': 'Описание', 'key_skills': 'Навыки', 'experience_id': 'Опыт работы', 'premium': 'Премиум-вакансия', 'employer_name': 'Компания', 'salary': 'Оклад', 'area_name': 'Название региона', 'published_at': 'Дата публикации вакансии'}

class DataSet:
	def __init__(self, file_name, vacancies_objects):
		self.file_name = file_name
		self.vacancies_objects = vacancies_objects

class Vacancy:
	def __init__(self, name, description, key_skills, experience_id, premium, employer_name, salary, area_name, published_at):
		self.name = name
		self.description = description
		self.key_skills: list = key_skills
		self.experience_id = experience_id
		self.premium = premium
		self.employer_name = employer_name
		self.salary: Salary = salary
		self.area_name = area_name
		self.published_at: datetime = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S+%f')

class Salary:
	def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
		self.salary_from = salary_from
		self.salary_to = salary_to
		self.salary_gross = salary_gross
		self.salary_currency = salary_currency

def format_value(dict_object: dict, key: str, value: str):
	value = re.sub('\r', '', value)
	value = re.sub(r'<[^>]+>', '', value, flags=re.S)
	value = '\n'.join(map(lambda i: i.strip(), value.split('\n'))) if '\n' in value else ' '.join(value.strip().split())
	
	if key == 'key_skills':
		dict_object[key] = value.split('\n')
	else:
		dict_object[key] = value

def parse_filter(data: str):
	if data == '':
		return [None, None]
	if ': ' in data:
		name, value = data.split(': ')
		inverse_title_names = {v: k for k, v in title_names.items()}

		if name in inverse_title_names.keys():
			name = inverse_title_names[name]
		if not name in inverse_title_names.values():
			return 'Параметр поиска некорректен'

		return [name, value]

	return 'Формат ввода некорректен'

def csv_reader(file_name: str):
	with open(file_name, 'r', encoding='utf-8', newline='') as file:
		titles = re.sub('\n|\r|\ufeff', '', file.readline()).split(',')
		data = [elem for elem in list(csv.reader(file)) if all(map(lambda x: len(x) > 0, elem)) and len(elem) == len(titles)]
		
		file.seek(0)
		if file.read() == '':
			return 'Пустой файл'
		if len(data) == 0:
			return DataSet(file_name, [])

	return titles, data

def csv_filer(titles: list, data: list):
	vacancies_objects = []

	for vacancy_data in data:
		vacancy = {key: ... for key in table_fields.keys()}
		salary = {key: ... for key in ('salary_from', 'salary_to', 'salary_gross', 'salary_currency')}
		for key, value in zip(titles, vacancy_data):
			format_value(salary if 'salary' in key else vacancy, key, value)

		vacancy['salary'] = Salary(**salary)
		vacancies_objects.append(Vacancy(**vacancy))

	return vacancies_objects


data: List[Vacancy] = csv_filer(*csv_reader('vacancies_dif_currencies.csv'))

oldest_vacancy = None
newest_vacancy = None

for vacancy in data:
	if not oldest_vacancy:
		oldest_vacancy = vacancy
	if not newest_vacancy:
		newest_vacancy = vacancy

	if vacancy.published_at < oldest_vacancy.published_at:
		oldest_vacancy = vacancy

	if vacancy.published_at > newest_vacancy.published_at:
		newest_vacancy = vacancy

print(f'Дата публикации самой старой вакансии: {oldest_vacancy.published_at}\nДата публикации самой новой вакансии: {newest_vacancy.published_at}')
