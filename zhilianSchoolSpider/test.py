from queue import Queue
from threading import Thread
from time import sleep

q = Queue()
NUM = 10
JOBS = 400


# 具体的处理函数，负责处理单个任务
def do_somthing_using(arguments):
    print(arguments)


# 这个是工作进程，负责不断从队列取数据并处理
def working():
    while True:
        arguments = q.get()
        do_somthing_using(arguments)
        sleep(3)
        q.task_done()
for i in range(JOBS):
    q.put(i)

# fork NUM个线程等待队列
for i in range(NUM):
    t = Thread(target=working)
    t.setDaemon(True)
    t.start()
# 把JOBS排入队列

# 等待所有JOBS完成
q.join()
