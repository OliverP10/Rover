import threading
from threading import Thread
import time

def test_func():
    time.sleep(10)
    print("done")

thread1 = Thread(target = test_func, args = ())
thread1.start()

while True:
    print("hi")
    time.sleep(0.5)



thread1.join()



    