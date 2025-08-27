import threading
from threading import *
# madea a class A inhering Thread
class A(threading.Thread):
    def run(self):
        for x in range(7):
            print("child =",current_thread().getName())
#create a object for class A
obj=A()
obj.start()
obj.join()
#after print 7 the main tread ran
print("Control returned to",current_thread().getName())