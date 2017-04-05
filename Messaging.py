
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
    def receive_message(self, callback):
        '''blockIO and wait for recieption of messages on queue'''
        def print_message(channel, method, properties, body):
            '''default case,
            just kick out print of the message
            '''
            print("fetched '%s' from %s" % \
                #decode is needed as amqp messages are bytestreams, not base strings
                  (body.decode('utf-8'), self.queue)
                 )

        #set up the default case of "print"
        if callback == "print":
            callback = print_message

        while 1:
            method_frame, header_frame, body = self.channel.basic_get(self.queue)
            print(method_frame)
            if method_frame:
                callback(self.channel, method_frame, header_frame, body)
                self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            else:
                return False


    def __del__(self):
        '''cleanup, what else?
        '''
        try:
            self.connection.close()
        except AttributeError:
            sys.stderr.write("connection didn't exist, nothing to do")


if __name__ == '__main__':
    THING = Messaging("hello")
    for n in range(1,10):
        THING.send_message(random.choice(['dude', 'sweet', 'whoa', 'awesome']))
    THING.receive_message('print')
    #grab the first arguement or send something generic
