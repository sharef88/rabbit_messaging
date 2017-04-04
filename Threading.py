#!/usr/bin/python3
'''
Teachin myself Threading
'''
from threading import Thread
import json
import Messaging

INDEX=int()

def decode(channel, method, properties, body):
    global INDEX
    out = json.loads(body.decode('utf-8'))
    INDEX = out['index']
    print(out['index'])

if __name__ == "__main__":
    #create the connection object
    CONN = Messaging.Messaging('hello1')

    #set up a thread to decode received messages
    T1 = Thread(target=CONN.receive_message, args=(decode,))

    #THREAD IS GO GO GO
    T1.start()

    #now that we got that outta the way, lets bounce some messages
    for i in range(1000):
        CONN.send_message({'index': i, 'other stuff':'yup'})
    #now we gotta wait for the bloody thing to finish receiving messages.
    #I'm sure there's a graceful way of using Thread.join here
    while INDEX < 999:
        pass
    del CONN
    