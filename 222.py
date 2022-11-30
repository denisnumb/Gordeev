import csv
import re
from itertools import islice
from typing import List, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from prettytable import PrettyTable, ALL

title_names = {'name': 'Название', 'description': 'Описание', 'key_skills': 'Навыки', 'experience_id': 'Опыт работы', 'premium': 'Премиум-вакансия', 'employer_name': 'Компания', 'salary': 'Оклад', 'salary_from': 'Нижняя граница вилки оклада', 'salary_to': 'Верхняя граница вилки оклада', 'salary_gross': 'Оклад указан до вычета налогов', 'salary_currency': 'Идентификатор валюты оклада', 'area_name': 'Название региона', 'published_at': 'Дата публикации вакансии'}
table_fields = {'name': 'Название', 'description': 'Описание', 'key_skills': 'Навыки', 'experience_id': 'Опыт работы', 'premium': 'Премиум-вакансия', 'employer_name': 'Компания', 'salary': 'Оклад', 'area_name': 'Название региона', 'published_at': 'Дата публикации вакансии'}
experience = {'noExperience': 'Нет опыта', 'between1And3': 'От 1 года до 3 лет', 'between3And6': 'От 3 до 6 лет', 'moreThan6': 'Более 6 лет'}
currency = {'AZN': 'Манаты', 'BYR': 'Белорусские рубли', 'EUR': 'Евро', 'GEL': 'Грузинский лари', 'KGS': 'Киргизский сом', 'KZT': 'Тенге', 'RUR': 'Рубли', 'UAH': 'Гривны', 'USD': 'Доллары', 'UZS': 'Узбекский сум'}
currency_to_rub = {'AZN': 35.68, 'BYR': 23.91, 'EUR': 59.9, 'GEL': 21.74, 'KGS': 0.76, 'KZT': 0.13, 'RUR': 1, 'UAH': 1.64, 'USD': 60.66, 'UZS': 0.0055}

class Vacancy:
	"""Класс для представления вакансии.

	Attributes:
		name (str): Название вакансии
		area_name (str): Название города, в котором представлена вакансия
		salary (Salary): Оклад вакансии
		published_at (datetime): Дата публикации вакансии
	"""
	def __init__(self, name, salary, area_name, published_at, **kwargs):
		"""Конструктор класса. Выполняет преобразование времени публикации к типу datetime
		
		Args:
			name (str): Имя вакансии
			salary (Salary): Оклад вакансии
			area_name (str): Название города, в котором представлена вакансия
			published_at (str): Дата публикации вакансии
		"""
		self.name: str = name
		self.area_name: str = area_name
		self.salary: Salary = salary
		self.published_at: datetime = datetime.strptime(published_at.replace('T', ' '), '%Y-%m-%d %H:%M:%S+%f')

class Salary:
	"""Класс для представления вакансии.

	Attributes:
		salary_from (SalaryFloatItem): Нижняя граница оклада
		salary_to (SalaryFloatItem): Верхняя граница оклада
		salary_currency (str): Валюта оклада
	"""
	def __init__(self, salary_from, salary_to, salary_currency, **kwargs):
		"""Конструктор класса. Выполняет преобразование float в SalaryFloatItem

		Args:
			salary_from (int or float): Нижняя граница оклада
			salary_to (int or float): Верхняя граница оклада
			salary_currency (str): Валюта оклада
		"""
		self.salary_from: SalaryFloatItem = SalaryFloatItem(salary_from)
		self.salary_to: SalaryFloatItem = SalaryFloatItem(salary_to)
		self.salary_currency: str = salary_currency

		if salary_currency != 'RUR':
			self.salary_from = currency_to_rub[salary_currency] * self.salary_from
			self.salary_to = currency_to_rub[salary_currency] * self.salary_to

	def __repr__(self):
		"""Возвращает строку с диапазоном и названием валюты оклада

		Returns:
			str: Текстовое представление класса
		"""
		return f'{self.salary_from} - {self.salary_to} ({self.salary_currency})'

	def __len__(self):
		"""Определяет значение длины экземляра класса

		Returns:
			int: Длина строки текстового представления класса
		"""
		return len(str(self))

class SalaryFloatItem(float):
	"""Класс для представления границы оклада вакансии.

	Attributes:
		value (int or float): Значение границы оклада
	"""

	def __repr__(self):
		"""Текстовое представление класса

		Returns:
			str: Возвращает число, у которого разряды разделены пробелом
		"""
		return f'{int(self):,}'.replace(',', ' ')


class Report:
	"""Класс для вывода визуальной статистики.

	Attributes:
		prof_name (str): Название профессии, для которой нужно выделить статистику
		salaries (dict): Статистика зарплат для всех профессий
		vacancies (dict): Статистика вакансий для всех профессий
		salaries_prof (dict): Статистика зарплат для prof_name
		vacancies_prof (dict): Статистика вакансий для prof_name
		cities_salaries (dict): Динамика зарплат в городах
		cities_vacancies (dict): Доля вакансий в городах
	"""
	def __init__(self, prof_name, salaries, vacancies, salaries_prof, vacancies_prof, cities_salaries, cities_vacancies):
		"""Конструктор класса
		
		Args:
			prof_name (str): Название профессии, для которой нужно выделить статистику
			salaries (dict): Статистика зарплат для всех профессий
			vacancies (dict): Статистика вакансий для всех профессий
			salaries_prof (dict): Статистика зарплат для prof_name
			vacancies_prof (dict): Статистика вакансий для prof_name
			cities_salaries (dict): Динамика зарплат в городах
			cities_vacancies (dict): Доля вакансий в городах
		"""
		self.prof_name = prof_name
		self.salaries = salaries
		self.vacancies = vacancies
		self.salaries_prof = salaries_prof
		self.vacancies_prof = vacancies_prof
		self.cities_salaries = cities_salaries
		self.cities_vacancies = cities_vacancies

	def __get_min_max(self, dict_):
		"""Приватный метод для получения минимального и максимального значений ключей словаря

		Returns:
			Tuple[int]: Первое значение — минимальное, Второе — максимальное 
		"""
		return min(dict_.keys()), max(dict_.keys())

	def generate_image(self):
		"""Метод генерации изображения, представляющего статистику
		"""
		salaries_start_year, salaries_last_year = self.__get_min_max(self.salaries)
		prof_salaries_start_year, prof_salaries_last_year = self.__get_min_max(self.salaries_prof)

		plt.figure(figsize=(12, 7))

		plt.subplot(2, 2, 1)
		plt.bar(np.arange(salaries_start_year, salaries_last_year+1) - 0.2, list(self.salaries.values()), width = 0.4)
		plt.bar(np.arange(prof_salaries_start_year, prof_salaries_last_year+1) + 0.2, list(self.salaries_prof.values()), width = 0.4)
		plt.legend(['средняя з/п', f'з/п {self.prof_name}'])
		plt.grid(axis='y')
		plt.title('Уровень зарплат по годам')
		plt.xticks(rotation=90)
	   
		vacancies_start_year, vacancies_last_year = self.__get_min_max(self.vacancies)
		prof_vacancies_start_year, prof_vacancies_last_year = self.__get_min_max(self.vacancies_prof)
		plt.subplot(2, 2, 2)
		plt.bar(np.arange(vacancies_start_year, vacancies_last_year+1) - 0.2, list(self.vacancies.values()), width = 0.4)
		plt.bar(np.arange(prof_vacancies_start_year, prof_vacancies_last_year+1) + 0.2, list(self.vacancies_prof.values()), width = 0.4)
		plt.legend(['Количество вакансий', f'Количество вакансий {self.prof_name}'])
		plt.grid(axis='y')
		plt.title('Количество вакансий по годам')
		plt.xticks(rotation=90)

		plt.subplot(2, 2, 3)
		plt.barh(list(self.cities_salaries.keys()), list(self.cities_salaries.values()))
		plt.grid(axis='x')
		plt.gca().invert_yaxis()
		plt.title('Уровень зарплат по городам')

		plt.subplot(2, 2, 4)
		other_cities = 1 - sum(self.cities_vacancies.values())
		plt.pie([other_cities]+list(self.cities_vacancies.values()), labels=['Другие']+list(self.cities_vacancies.keys()), normalize=False)
		plt.axis("equal")
		plt.title('Доля вакансий по городам')
	   
		plt.subplots_adjust(wspace=.4, hspace=.4)
		plt.savefig('graph.png')
		plt.show()

def csv_reader(file_name: str) -> Tuple[List[str], List[str]]:
	"""Читает csv-файл и возвращает его заголовки и значения строк

	Args:
		file_name (str): Название csv-файла

	Returns:
		Tuple[List[str], List[str]]: Первый индекс — заголовки, Второй — значения строк
	"""
	with open(file_name, 'r', encoding='utf-8', newline='') as file:
		titles = re.sub('\n|\r|\ufeff', '', file.readline()).split(',')
		data = [elem for elem in list(csv.reader(file)) if all(map(lambda x: len(x) > 0, elem)) and len(elem) == len(titles)]
	   
		file.seek(0)
		if file.read() == '':
			return 'Пустой файл'
		if len(data) == 0:
			return 'Нет данных'

	return titles, data

def format_value(dict_object: dict, key: str, value: str) -> None:
	"""Форматирует значение и устанавливает его как значение определенного ключа для словаря

	Args:
		dict_object (dict): Словарь, в который нужно поставить значение
		key (str): Ключ для словаря
		value (str): Значение для словаря, которое нужно привести в читабельный вид
	"""
	value = re.sub('\r', '', value)
	value = re.sub(r'<[^>]+>', '', value, flags=re.S)
	value = '\n'.join(map(lambda i: i.strip(), value.split('\n'))) if '\n' in value else ' '.join(value.strip().split())    
	dict_object[key] = value

def csv_filer(titles: List[str], data: List[str]) -> List[Vacancy]:
	"""Формирует список вакансий из прочитанного csv-файла

	Args:
		titles (list): Заголовки csv-файла
		data (list): Данные строк csv-файла

	Returns:
		List[Vacancy]: Список вакансий
	"""
	vacancies_objects = []

	for vacancy_data in data:
		vacancy = {key: ... for key in ('name', 'area_name', 'published_at')}
		salary = {key: ... for key in ('salary_from', 'salary_to', 'salary_currency')}
		for key, value in zip(titles, vacancy_data):
			format_value(salary if 'salary' in key else vacancy, key, value)

		vacancy['salary'] = Salary(**salary)
		vacancies_objects.append(Vacancy(**vacancy))

	return vacancies_objects

def add_data(dict_object: dict, key: str, average_salary: float, add_empty: bool) -> None:
	"""Добавляет новые значения в словарь при формировании статистики

	Args:
		dict_object (dict): Объект словаря, в который нужно добавить данные
		key (str): Ключ словаря, для которого нужно добавить данные 
		average_salary (float): Среднее значенеи оклада
		add_empty (bool): Нужно ли обнулить данные для указанного ключа
	"""
	if add_empty:
		dict_object[key] = {'salary': [], 'count': 0}
	dict_object[key]['salary'].append(average_salary)
	dict_object[key]['count'] += 1

def calculate_average_salary(dict_object: dict) -> None:
	"""Заменяет в словаре значение оклада на среднее значение оклада

	Args:
		dict_object (dict): Объект словаря, в котором нужно обновить данные
	"""
	for key in dict_object:
		dict_object[key]['salary'] = int(sum(dict_object[key]['salary']) / len(dict_object[key]['salary']))

def print_vacancies(vacancies_data: list, filter_: list, sort_param: str, reverse_sort: bool, numbers: list, columns: list):
	"""Выводит на экран таблицу вакансий

	Args:
		vacancies_data (list): Список вакансий
		filter_ (list): [0] — Ключ для фильтрации таблицы, [1] — Значение для фильтрации таблицы
		sort_param (list): Параметр сортировки 
		reverse_sort (bool): Сортировать в обратном порядке
		numbers (list): Диапазон строк таблицы, которые нужно выводить
		columns (list): Названия колонок таблицы, которые нужно выводить
	"""
	table = PrettyTable(hrules=ALL, field_names=list(table_fields.values()), max_width=20, align='l')
	filter_key, filter_value = filter_

	if sort_param:
		vacancies_data = sorted(vacancies_data, key= lambda v: apply_sort(sort_param, v), reverse=reverse_sort)

	for vacancy in vacancies_data:
		if filter_key and not apply_filter(filter_key, filter_value, vacancy):
			continue
		table.add_row([str(v)[:100]+'...' if len(str(v)) > 100 else str(v) for k, v in vacancy.__dict__.items() if k in table_fields.keys()])	
	
	if len(table.rows) == 0:
		return print('Ничего не найдено')

	table.add_autoindex('№')

	end = numbers[1] if len(numbers) == 2 else len(table.rows)
	columns = list(table_fields.values()) if len(columns) == 0 else [field for field in table_fields.values() if field in columns]
	print(table.get_string(start=numbers[0], end=end, fields=['№']+columns))

def parse_filter(data: str):
	"""Возвращает параметр филтрации, извлеченный из пользовательского ввода

	Args:
		data (str): Пользовательский ввод, подразумевающий параметр фильтрации

	Returns:
		list or str: Список, если запрос `data` корректен, Строка — если некорректен
	"""
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

def apply_filter(key, filter_value, vacancy):
	"""Определяет, соответствует ли вакансия параметру фильтрации

	Args:
		key (str): Ключ фильтра
		filter_value (Any): Значение фильтра
		vacancy (Vacancy): Вакансия, к которой нужно применить фильтр

	Returns:
		bool: Нужно ли выводить вакансию в таблицу
	"""
	if key == 'salary':
		return vacancy.salary.salary_from <= float(filter_value) <= vacancy.salary.salary_to
	if key == 'key_skills':
		return all(map(lambda i: i in vacancy.key_skills.split('\n'), filter_value.split(', ')))
	if key == 'published_at':
		return filter_value == str(vacancy.published_at)
	return filter_value == (vacancy.__dict__[key] if key in vacancy.__dict__ else vacancy.salary.__dict__[key])

def apply_sort(sort_param: str, vacancy: Vacancy):
	"""Подготавливает значение для сравнения с другим значением при сортировке

	Args:
		sort_param (str): Параметр сортировки
		vacancy (Vacancy): Вакансия, к которой применяется сортировка

	Returns:
		Any: Значение для сравнения с другим значением при сортировке
	"""
	if sort_param == 'key_skills':
		return len(vacancy.key_skills.split('\n'))
	if sort_param == 'experience_id':
		return {v: i for i, v in enumerate(experience.values())}[vacancy.experience_id]
	if sort_param == 'salary':
		currency_multiplier = currency_to_rub[{v: k for k, v in currency.items()}[vacancy.salary.salary_currency]]
		return (vacancy.salary.salary_from * currency_multiplier + vacancy.salary.salary_to * currency_multiplier) / 2
	return vacancy.__dict__[sort_param]

def print_statistics(vacancies_data: List[Vacancy], prof_name: str) -> None:
	"""Вычисляет и создает файл визуального представления статистики

	Args:
		vacancies_data (list): Список вакансий
		prof_name (str): Название профессии, для которой нужно подсчитать отдельную статистику
	"""
	total_data = {}
	prof_data = {}
	cities = {}

	for vacancy in vacancies_data:
		average_salary = (vacancy.salary.salary_from + vacancy.salary.salary_to) / 2
		# статистика городов
		add_data(cities, vacancy.area_name, average_salary, vacancy.area_name not in cities.keys())
		# зарплаты и вакансии
		add_data(total_data, vacancy.published_at.year, average_salary, vacancy.published_at.year not in total_data.keys())
		# зарплаты и вакансии для профессии
		if prof_name in vacancy.name:
			add_data(prof_data, vacancy.published_at.year, average_salary, vacancy.published_at.year not in prof_data.keys())

	for dict_ in (total_data, prof_data, cities):
		calculate_average_salary(dict_)

	# убираем все города, в которых количество вакансий меньше 1% от общего числа вакансий
	cities = {k: v for k, v in cities.items() if (lambda v: 1 if v >= 0.75 else 0)(cities[k]['count'] / len(vacancies_data) * 100) >= 1}

	salaries = {year: total_data[year]["salary"] for year in total_data}
	vacancies = {year: total_data[year]["count"] for year in total_data}
	salaries_prof = {year: prof_data[year]["salary"] for year in prof_data}
	vacancies_prof = {year: prof_data[year]["count"] for year in prof_data}

	print('Динамика уровня зарплат по годам:', salaries)
	print('Динамика количества вакансий по годам:', vacancies)
	print('Динамика уровня зарплат по годам для выбранной профессии:', salaries_prof)
	print('Динамика количества вакансий по годам для выбранной профессии:', vacancies_prof)
	top10 = dict(islice({k: v for k, v in sorted(cities.items(), key=lambda item: item[1]['salary'], reverse=True)}.items(), 10))
	salaries_cities_to_print = {k: top10[k]['salary'] for k in top10}
	print('Уровень зарплат по городам (в порядке убывания):', salaries_cities_to_print)
	top10 = dict(islice({k: v for k, v in sorted(cities.items(), key=lambda item: item[1]['count'], reverse=True)}.items(), 10))
	vacancies_cities_to_print = {k: float(f"{(top10[k]['count'] / len(vacancies_data)):.4f}") for k in top10}
	print('Доля вакансий по городам (в порядке убывания):', vacancies_cities_to_print)

	Report(prof_name, salaries, vacancies, salaries_prof, vacancies_prof, salaries_cities_to_print, vacancies_cities_to_print).generate_image()

def get_input2():
	"""Запрашивает пользовательский ввод для формирования текстовой статистики
	"""
	file_name = input('Введите название файла: ')
	filter_ = parse_filter(input('Введите параметр фильтрации: '))
	sort_param = input('Введите параметр сортировки: ')
	reverse_sort = input('Обратный порядок сортировки (Да / Нет): ').lower()
	numbers_to_print = list(map(lambda i: int(i)-1, input('Введите диапазон вывода: ').split())) or [0]
	columns_to_print = list(filter(None, input('Введите требуемые столбцы: ').split(', ')))	

	if isinstance(filter_, str):
		return print(filter_)
	if sort_param and not sort_param in table_fields.values():
		return print('Параметр сортировки некорректен')
	if not reverse_sort in ('да', 'нет', ''):
		return print('Порядок сортировки задан некорректно')
	csv_data = csv_reader(file_name)
	if isinstance(csv_data, str):
		return print(csv_data)

	sort_param = {v: k for k, v in table_fields.items()}[sort_param] if sort_param else ''
	print_vacancies(csv_filer(*csv_data), filter_, sort_param, reverse_sort == 'да', numbers_to_print, columns_to_print)

def get_input1():
	"""Запрашивает пользовательский ввод для формирования файла визуальной статистики
	"""
	file_name = input('Введите название файла: ')
	prof_name = input('Введите название профессии: ')

	csv_data = csv_reader(file_name)
	if isinstance(csv_data, str):
		return print(csv_data)

	print_statistics(csv_filer(*csv_data), prof_name)


def get_input():
	"""Запрашивает пользовательский выбор результата работы программы
	"""
	choice = input('Вакансии или Стастистика: ')
	if choice == 'Вакансии':
		return get_input2()
	if choice == 'Статистика':
		return get_input1()


get_input()