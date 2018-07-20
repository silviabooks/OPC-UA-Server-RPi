# FROM: https://docs.python.org/3/library/threading.html#rlock-objects

import threading

lock = threading.RLock()

def func1():
    with lock:
        func2()

def func2():
    with lock: # this does not block even though the lock is acquired already
        print 'hello world'

# **** OPPURE *****

# http://www.bogotobogo.com/python/Multithread/python_multithreading_Using_Locks_with_statement_Context_Manager.php

# https://docs.python.org/2.5/whatsnew/pep-343.html

# Questo sembra molto buono
#https://www.laurentluce.com/posts/python-threads-synchronization-locks-rlocks-semaphores-conditions-events-and-queues/
