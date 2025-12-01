import threading
import time

shared_number = 0


def thread_1(number):
    global shared_number
    print("thread_1 number = ", end=""), print(number)

    for i in range(number):
        shared_number += 1
    print("thread_1 number end")

def thread_2(number):
    global shared_number
    print("thread_2 number = ", end=""), print(number)

    for i in range(number):
        shared_number += 1
    print("thread_2 number end")

def thread_3(number):
    global shared_number
    print("thread_2 number = ", end=""), print(number)

    for i in range(number):
        shared_number += 1
    print("thread_3 number end")

if __name__ == "__main__":

    threads = []

    start_time = time.time()
    t1 = threading.Thread(target=thread_1, args=(10000000,)) #천만
    t1.start()
    threads.append(t1)

    t2 = threading.Thread(target=thread_2, args=(10000000,)) #천만
    t2.start()
    threads.append(t2)
    
    t3 = threading.Thread(target=thread_3, args=(10000000,)) #천만
    t3.start()
    threads.append(t3)

    for t in threads:
        t.join() # 쓰레드가 모든 작업을 마칠 때까지 기다리는 것

    print("--- %s seconds ---" % (time.time() - start_time))

    print("shared_number=", end=""), print(shared_number)
    print("end of main")
    