#!/usr/bin/python3
'''thisis a docstring for the testing module, go away'''
import random
import Messaging


def print_message(channel, method, header, body):
    '''
    default case,
    just kick out print of the message
    '''
    channel, header = channel, header
    #decode is needed as amqp messages are bytestreams, not base strings
    print("Message %s fetched '%s'    \tfrom %s" %
          (method.delivery_tag, body.decode('utf-8'), method.routing_key))
    return body.decode('utf-8')

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
    msg_count = 10
    for _ in range(0, msg_count):
        conn.send_message(
            message=random.choice(['dude', 'sweet', 'whoa', 'awesome']),
            key=key
            )
    #recieve messages and print the return code
    results = conn.receive_message(
        callback=print_message,
        loop=0)
    #elaborate on the output
    print(results)
    if results['sent'] == msg_count:
        out = "all the messages returned successfully"
    else:
        out = "%s messages were not sent" % (msg_count-results['sent'])
    print(out)
    conn.close()

if __name__ == '__main__':
    test('hello.test.message')
