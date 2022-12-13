import os
from stats import *
import concurrent.futures as pool

files = [f'C:/users/denisnumb/desktop/vacancies/{file}' for file in os.listdir('C:/users/denisnumb/desktop/vacancies')]
with pool.ThreadPoolExecutor() as executor:
	executor.map(get_input, files)