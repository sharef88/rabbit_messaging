#!/usr/bin/python3
'''Module for building a pika-amqp connection'''
import sys
import ssl
import json
import random
import pika
__author__ = "sharef88"

class Messaging(object):
    ''' Class for setting up an AMQP Connection
    '''
    @staticmethod
    def _open_config():
        ''' open the config.json file that is in the same directory and de-serialize its contents.
        it will also check type-sanity
        '''
        with open("config.json", 'r') as fin:
            config = json.load(fin)
            config['port'] = int(config['port'])
            config['credentials'] = pika.PlainCredentials(**config['credentials'])
            config['ssl_options']['ssl_version'] = ssl.PROTOCOL_TLSv1_2
            config['ssl_options']['cert_reqs'] = ssl.CERT_REQUIRED
            return config

    def __init__(self, queue):
        ''' This function will configure self.connection and self.channel for normal usage
        '''
        #Create the connection using data from the config file
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(**self._open_config()))

        #set up the internal variables
        self.queue = queue
        self.channel = self.connection.channel()
        self.queue_object = self.channel.queue_declare(
            queue=queue,
            durable=True,
            exclusive=False,
            auto_delete=False
            )
        self.waiting_messages = self.queue_object.method.message_count

    def send_message(self, message):
        '''
        Send message to self.channel,
        will always json-serialize the message to best facilitate reception of the message
        '''

        #serialize the message into json
        message = json.dumps(message)
        #publish the message to the queue "routing key" via "exchange"
        #this is largely amqp/rabbit naming convention
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=message
        )
        self.waiting_messages = self.queue_object.method.message_count
    def receive_message(self, callback, loop):
        '''
        Receive Messages:
        Callback function is used 'pon the message, default case is "print"
        #
        loop the reception while:
        -- loop == -1 -> loop infinitely
        -- loop == 0 -> loop until queue is empty
        -- loop == n -> loop until received n messages
        '''
        #convert a loop statement to timeout
        if loop == 0:
            timeout = 2 #if loop until empty then set a timeout to grab the "empty" state
        else:
            timeout = None
        self.channel.basic_qos(prefetch_count=2)
        sent_messages = 0
        #Try: statement is for catching the Nonetype not iterable error that this would cause
        try:
            for method, header, body in self.channel.consume(
                    queue=self.queue,
                    inactivity_timeout=timeout,
                ):

                callback(self.channel, method, header, body)  #do the thing, you know, the thing!
                sent_messages = method.delivery_tag           #Make sure you record the thing-doing!
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
                #yessir, I've done the thing

                #kill the loop 'pon conditions stated above
                if loop == method.delivery_tag:
                    break
        except TypeError:
            pass
        #return a report of sent messages
        requeued = self.channel.cancel()
        self.channel.close()
        return {
            'sent': sent_messages,
            'requeued': requeued,
            }


    def __del__(self):
        '''
        cleanup, what else?
        '''
        try:
            self.connection.close()
        except AttributeError:
            print("connection didn't exist, nothing to do", file=sys.stderr)

def print_message(channel, method, header, body):
    '''
    default case,
    just kick out print of the message
    '''
    channel, header = channel, header
    #decode is needed as amqp messages are bytestreams, not base strings
    print("Message %s fetched '%s' from %s" %
          (method.delivery_tag, body.decode('utf-8'), method.routing_key))

if __name__ == '__main__':
    #set up a connection to the hello queue
    THING = Messaging("hello")
    #send a pile o messages
    print('And now! we test! FOR SCIENCE')
    for n in range(0, 1000):
        THING.send_message(random.choice(['dude', 'sweet', 'whoa', 'awesome']))
    #recieve messages and print the return code
    print(THING.receive_message(print_message, 0))
