import csv
import re
from datetime import datetime
from typing import Tuple, List


def csv_reader(file_name: str) -> Tuple[List[str], List[str]]:
	with open(file_name, 'r', encoding='utf-8', newline='') as file:
		titles = re.sub('\n|\r|\ufeff', '', file.readline()).split(',')
		return titles, [elem for elem in list(csv.reader(file)) if all(map(lambda x: len(x) > 0, elem)) and len(elem) == len(titles)]


def get_year(vacancy_data) -> int:
	return datetime.strptime(vacancy_data[-1], '%Y-%m-%dT%H:%M:%S+%f').year

year_values = {}

titles, vacancies = csv_reader('C:/users/denisnumb/desktop/vacancies_by_year.csv')

for vacancy in vacancies:
	year = get_year(vacancy)

	if year not in year_values.keys():
		year_values[year] = []

	year_values[year].append(vacancy)


for year, rows in year_values.items():
	with open(f'C:/users/denisnumb/desktop/vacancies/{year}.csv', 'w', encoding='utf-8') as file:
		writer = csv.writer(file)
		writer.writerow(titles)
		writer.writerows(rows)