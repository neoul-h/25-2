#single thread
import time

def thread_first():
    print("the first thread starts")
    for i in range(5):
        print(f"thread_1 : {i}")
        time.sleep(0.1)
    print("the first thread ends")

def thread_second():
    print("the second thread starts")
    for i in range(5):
        print(f"thread_2 : {i}")
        time.sleep(0.1)
    print("the second thread ends")

def thread_third():
    print("the third thread starts")
    for i in range(5):
        print(f"thread_3 : {i}")
        time.sleep(0.1)
    print("the third thread ends")

class Timer():
    def __init__(self):
        self.start_time = time.time()
        self.end_time = None

    def end(self):
        self.end_time = time.time()
        print(f"time spent {self.end_time - self.start_time}")

timer = Timer()

thread_first()
thread_second()
thread_third()

timer.end()