#!/usr/bin/python3
'''Module for building a pika-amqp connection'''
import sys
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
        #seriously, pylint can shut up about the callback structure
        def print_message(channel, method, header, body):
            '''default case,
            just kick out print of the message
            '''
            #decode is needed as amqp messages are bytestreams, not base strings
            print("fetched '%s' from %s" % (body.decode('utf-8'), self.queue))
            #print([channel.get_waiting_message_count(), method.delivery_tag])
            print([self.queue_object.method.message_count, method.delivery_tag])

        #set up the default case of "print"
        if callback == "print":
            callback = print_message

        #loop the reception while:
        # -- loop == -1 -> loop infinitely
        # -- loop == 0 -> loop until queue is empty
        # -- loop == n -> loop until received n messages
        for method, header, body in self.channel.consume(self.queue):
            #do the thing, you know, the thing!
            callback(self.channel, method, header, body)
            #yessir, I've done the thing
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

            #kill the loop 'pon conditions stated above
            #print([message_count,method.delivery_tag])
                    #loop == 0 and not self.channel.get_waiting_message_count():
            if loop == method.delivery_tag or \
                    loop == 0 and self.waiting_messages == method.delivery_tag:
                sent_messages = method.delivery_tag
                requeued = self.channel.cancel()
                break
        #return a report of sent messages
        self.channel.close()
        return {
            'sent': sent_messages,
            'requeued': requeued,
            'waiting': self.queue_object.method.message_count
            }


    def __del__(self):
        '''
        cleanup, what else?
        '''
        try:
            self.connection.close()
        except AttributeError:
            print("connection didn't exist, nothing to do", file=sys.stderr)


if __name__ == '__main__':
    #set up a connection to the hello queue
    THING = Messaging("hello")
    #send a pile o messages
    #for n in range(0, 1000):
    #    THING.send_message(random.choice(['dude', 'sweet', 'whoa', 'awesome']))
    #recieve messages and print the return code
    out = THING.receive_message('print', 0)
    print(out)
