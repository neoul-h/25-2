import threading

_lock = threading.Lock()
class TestClass:
    def __init__(self):
        self.count = 0

def lets_go(i, c):
    print(f'[Thread {i}] Started (id : {threading.get_ident()})')
    _lock.acquire()
    for j in range(5):
        c.count = c.count + 1
        print(f'[Thread {i}] {c.count}')
    _lock.release()


if __name__ == "__main__":
    tc = TestClass()
    for i in range(5):
        th = threading.Thread(target=lets_go, args=[i, tc])
        th.start()