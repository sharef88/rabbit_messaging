#!/usr/bin/python3.4
'''Module for building a pika-amqp connection'''
import sys
import json
import pika
__author__ = "sharef88"

class Messaging:
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

        #open the config file, deserialize it from json to w/else:
        #with will auto- __exit__ its with'd object
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(**self._open_config())
            )
        except ConnectionError as err:
            sys.stderr.write('ERROR: %sn' % str(err))
            print("Could not connect")

        #set up the internal variables
        self.queue = queue
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)

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
            routing_key='hello',
            body=message
        )
    def receive_message(self, callback):
        '''blockIO and wait for recieption of messages on queue'''
        def print_message(body):
            '''default case,
            just kick out print of the message
            '''
            print("fetched '%s' from %s" % \
                #decode is needed as amqp messages are bytestreams, not base strings
                  (body.decode('utf-8'), self.queue)
                 )
        if callback == "print":
            callback = print_message

        self.channel.basic_consume(
            consumer_callback=callback,
            queue=self.queue,
            no_ack=True
        )
        print("Waiting for Messages on '%s'" % self.queue)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()


    def __del__(self):
        '''cleanup, what else?
        '''
        try:
            self.connection.close()
        except AttributeError:
            sys.stderr.write("connection didn't exist, nothing to do")


if __name__ == '__main__':
    THING = Messaging("hello")
    THING.send_message("dude")
    #grab the first arguement or send something generic
    #THING.receive_message('print')
    #del THING
