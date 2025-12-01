#https://docs.python.org/ko/3/library/threading.html
import threading
import time

shared_number = 0
lock = threading.Lock()  # threading에서 Lock 함수 가져오기


def thread_1(number):
    global shared_number
    print("thread_1 number = ", end=""), print(number)

    
    for i in range(number):
        lock.acquire()  # 작업이 끝나기 전까지 다른 쓰레드가 공유데이터 접근을 금지
        shared_number += 1
        lock.release()  # lock 해제


def thread_2(number):
    global shared_number
    print("thread_2 number = ", end=""), print(number)


    for i in range(number):
        lock.acquire()  # 작업이 끝나기 전까지 다른 쓰레드가 공유데이터 접근을 금지
        shared_number += 1
        lock.release()  # thread_2 해제


if __name__ == "__main__":

    threads = []

    start_time = time.time()
    t1 = threading.Thread(target=thread_1, args=(10000000,)) #천만
    t1.start() # start() 함수로 쓰레드를 시작
    threads.append(t1)

    t2 = threading.Thread(target=thread_2, args=(10000000,)) #천만
    t2.start()
    threads.append(t2)

    for t in threads:
        t.join() # 쓰레드가 모든 작업을 마칠 때까지 기다리는 것

    print("--- %s seconds ---" % (time.time() - start_time))

    print("shared_number=", end=""), print(shared_number)
    print("end of main")