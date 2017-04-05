#!/usr/bin/python3
'''
Teachin myself Threading
'''
from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool
import json
import time
import Messaging

def calc_sqr(channel, method, properties, body):
    '''calculates the square of the json-index'''
    x = int(json.loads(body.decode('utf-8'))['index'])
    print([x,x*x])
    time.sleep(1)

def worker(conn):
    conn.receive_message(calc_sqr, 0)

if __name__ == "__main__":
    CONN = Messaging.Messaging('hello1')
    #now that we got that outta the way, lets bounce some messages
    print("Filling the queue")
    for i in range(100):
        CONN.send_message({'index': i, 'other stuff':'yup'})
    del CONN
    #now we gotta wait for the bloody thing to finish receiving messages.
    #set up a thread to decode received messages
    timing=list()
    t1=time.time()

    pool = ThreadPool(20)
    CONNECTIONS = list()
    print('Making tons of threads')
    for i in range(20):
        CONNECTIONS.append(Messaging.Messaging('hello1'))
    timing.append(str(time.time()-t1))

    t2=time.time()
    pool.map(worker, CONNECTIONS)
    pool.close()
    pool.join()
    timing.append(str(time.time()-t2))
    timing.append(str(time.time()-t1))
    print(timing)

    print('done')
