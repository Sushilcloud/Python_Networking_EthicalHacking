from threading import *

def new():
    for x in range(6):
        print("child excuting ...",current_thread().getName())
t1=Thread(target=new)
# print current thread before the child thread has start
print(current_thread().getName())
t1.start()
# the main thread is waiting untill the child has finieshed
t1.join()
# Current thread().getName() mehtod for showing which tread is running
print("Bye",current_thread().getName())