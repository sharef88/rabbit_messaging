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
            pika.ConnectionParameters(**self._open_config())
        )

        #set up the internal variables
        self.queue = queue
        self.channel = self.connection.channel()
        self.queue_object = self.channel.queue_declare(
            queue=queue,
            durable=True,
            exclusive=False,
            auto_delete=False
            )

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

        #set up the default case of "print"
        if callback == "print":
            callback = print_message

        count = [1, 0]
        #loop the reception while:
        # -- loop == -1 -> loop infinitely
        # -- loop == 0 -> loop until queue is empty
        # -- loop == n -> loop until received n messages
        while \
                loop == -1 \
                or (loop == 0 and count[0]) \
                or count[1] < loop:
            method, header, body = self.channel.basic_get(self.queue)
            if method:
                #expose the remaining messages in queue
                count[0] = method.message_count
                #increment the total sent messages
                count[1] += 1

                #implement the callback function
                callback(self.channel, method, header, body)

                #send the all-clear that we got (and processed) the message
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                #edge-case, reset count to 0, as we did receive nada
                break
        print(count, loop)
        if count[1]:
            return True
        return False



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
    for n in range(0, 10):
        THING.send_message(random.choice(['dude', 'sweet', 'whoa', 'awesome']))
    #recieve messages and print the return code
    print(THING.receive_message('print', 0))
