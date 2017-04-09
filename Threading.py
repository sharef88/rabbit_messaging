#!/usr/bin/python3
'''
Teachin myself Threading
'''
from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool
import json
import time
import Messaging

def worker(conn):
    def calc_sqr(channel, method, properties, body):
        '''calculates the square of the json-index'''
        x = int(json.loads(body.decode('utf-8'))['index'])
        print([x, x ** 3])
    conn.receive_message(calc_sqr, 0)

if __name__ == "__main__":
    CONN = Messaging.Messaging(exchange='hello', routing='hello.thread')
    #set up a thread to decode received messages
    timing = list()
    t1 = time.time()

    pool = ThreadPool(10)
    CONNECTIONS = list()
    print('Making tons of threads')
    for i in range(10):
        CONNECTIONS.append(Messaging.Messaging(exchange='hello', routing='hello.thread'))
    timing.append(str(time.time()-t1))

    t2 = time.time()
    pool.map_async(worker, CONNECTIONS)
    timing.append(str(time.time()-t2))
    pool.close()

    #now that we got that outta the way, lets bounce some messages
    print("Filling the queue")
    for i in range(10000):
        CONN.send_message({'index': i, 'other stuff':'yup'}, 'hello.thread')
    del CONN
    #now we gotta wait for the bloody thing to finish receiving messages.
    
    pool.join()
    timing.append(str(time.time()-t2))
    timing.append(str(time.time()-t1))
    print(timing)

    for i in enumerate(CONNECTIONS):
        i[1].close()
    print('done')
