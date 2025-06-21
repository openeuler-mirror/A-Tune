import time
from src.utils.thread_pool import SerialTaskManager


def task1():
    time.sleep(10)
    return "Task 1 completed"


def task2():
    time.sleep(40)
    return "Task 2 completed"


def task3(x, y):
    return x + y

start_time = time.time()
manager = SerialTaskManager()
manager.add_task(task1)
manager.add_task(task2)
manager.add_task(task3, 5, 7)

results = manager.get_all_results()
for result in results:
    print(result)

end_time = time.time()
print(f"cost time {end_time - start_time} s")
