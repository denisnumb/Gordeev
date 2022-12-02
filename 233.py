from datetime import datetime
from time import time

class MyDateTime:
	def __init__(self, datetime_str: str) -> None:
		_date, _time = datetime_str.split()
		self.year, self.month, self.day = [int(x) for x in _date.split('-')]
		_time, microseconds = _time.split('.')
		self.microseconds = int(microseconds)
		self.hours, self.minutes, self.seconds = [int(x) for x in _time.split(':')]

	def __str__(self):
		year, month, day = (self).split('-')
		return f'{day[:2]}.{month}.{year}'

# декоратор для замеров времени выполнения
def print_func_exec_time(func) -> None:
	def wrapper(*args):
		start = time()
		func(*args)
		print(f'Время выполнения функции \'{func.__name__}\': {time() - start}')
	return wrapper

@print_func_exec_time
def str_to_datetime1(datetime_str: str) -> None:
	for _ in range(1000):
		datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')

@print_func_exec_time
def str_to_datetime2(datetime_str: str) -> None:
	for _ in range(1000):
		MyDateTime(datetime_str)

time_to_test = str(datetime.now())
str_to_datetime1(time_to_test)
str_to_datetime2(time_to_test)
# придумал только 2 варианта
#
# Вывод:
# Время выполнения функции 'str_to_datetime1': 0.025415658950805664
# Время выполнения функции 'str_to_datetime2': 0.0049550533294677734