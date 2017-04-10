#!/usr/bin/python3
'''thisis a docstring for the testing module, go away'''
import sys
import random
import json
from collections import Counter
import Messaging


def print_message(channel, method, header, body):
    '''
    default case,
    just kick out print of the message
    '''
    channel, header = channel, header
    #decode is needed as amqp messages are bytestreams, not base strings
    #print("Message %s fetched '%s'    \tfrom %s" %
    #      (method.delivery_tag, body.decode('utf-8'), method.routing_key))
    return (json.loads(body.decode('utf-8'))['message'], method.routing_key)

def test(key):
    '''
    test the stuff
    '''
    #set up a connection to the hello queue
    conn = Messaging.Messaging(
        exchange="hello",
        routing=key
        )

    #send a pile o messages
    print('And now! we test! FOR SCIENCE')
    msg_count = int(sys.argv[1])
    for i in range(0, msg_count):
        message = {
            'index':i,
            'message': random.choice(['dude', 'sweet', 'whoa', 'awesome'])
            }
        conn.send_message(
            message=message,
            key=key
            )
    #recieve messages and print the return code
    results = list()
    for i in conn.receive_message(
            callback=print_message,
            loop=0):
        results.append(i[0])
    #elaborate on the output
    print(Counter(results))
    conn.close()

if __name__ == '__main__':
    test('hello.test.message')
