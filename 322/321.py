import os
from stats import *
from multiprocessing import Process

if __name__ == '__main__':
	prof_name = input('Введите название профессии: ')
	for file in os.listdir('C:/users/denisnumb/desktop/vacancies'):
		Process(target=get_input, args=(f'C:/users/denisnumb/desktop/vacancies/{file}', prof_name)).start()