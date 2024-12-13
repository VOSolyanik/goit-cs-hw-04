import os
import time
import threading
from multiprocessing import Process, Queue
from queue import Queue as ThreadQueue

# Функція для пошуку ключових слів у файлі
def search_keywords_in_file(file_path, keywords):
    results = {keyword: [] for keyword in keywords}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for keyword in keywords:
                if keyword in content:
                    results[keyword].append(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return results


def worker(files, keywords, queue):
	local_results = {keyword: [] for keyword in keywords}
	for file in files:
		file_results = search_keywords_in_file(file, keywords)
		for keyword, paths in file_results.items():
			local_results[keyword].extend(paths)
	queue.put(local_results)

# Функція для об'єднання результатів
def combine_results(results_queue, keywords):
    final_results = {keyword: [] for keyword in keywords}
    while not results_queue.empty():
        local_results = results_queue.get()
        for keyword, paths in local_results.items():
            final_results[keyword].extend(paths)
    return final_results

# Багатопотокова версія
def multithreading_approach(file_list, keywords):
    num_threads = min(4, len(file_list))
    file_chunks = [file_list[i::num_threads] for i in range(num_threads)]
    results_queue = ThreadQueue()
    threads = []

    for chunk in file_chunks:
        thread = threading.Thread(target=worker, args=(chunk,keywords,results_queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return combine_results(results_queue, keywords)

# Багатопроцесорна версія
def multiprocessing_approach(file_list, keywords):
    num_processes = min(4, len(file_list))
    file_chunks = [file_list[i::num_processes] for i in range(num_processes)]
    results_queue = Queue()
    processes = []

    for chunk in file_chunks:
        process = Process(target=worker, args=(chunk, keywords, results_queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    return combine_results(results_queue, keywords)

# Вимірювання часу та тестування
def main():
    # Задаємо параметри
    directory = 'test-files'
    keywords = ['[ERROR]', '[WARN]', '[INFO]']
    file_list = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    print(f"Знайдені файли: {file_list}")  

    print("\nЗапуск Багатопотокового підходу...")
    start_time = time.time()
    threading_results = multithreading_approach(file_list, keywords)
    threading_time = time.time() - start_time

    print("Результат:\n", threading_results)
    print(f"Час виконання: {threading_time:.2f} секунд")

    print("\nЗапуск Багатопроцесорного підходу...")
    start_time = time.time()
    multiprocessing_results = multiprocessing_approach(file_list, keywords)
    multiprocessing_time = time.time() - start_time

    print("Результат:\n", multiprocessing_results)
    print(f"Час виконання: {multiprocessing_time:.2f} секунд")

if __name__ == '__main__':
    main()
