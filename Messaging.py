#!/usr/bin/python3.4
'''Module for building a pika-amqp connection'''
import sys
import pika
__author__ = "sharef88"

MESSAGE_HOST = pika.ConnectionParameters(
    host='192.168.1.155',
    port=5672,
    virtual_host='/',
    connection_attempts=1,
    credentials=pika.PlainCredentials(
        "guest",
        "guest"
    )
)
class Messaging:
    ''' Class for setting up an AMQP Connection
    '''
    def __init__(self, queue):
        ''' This function will configure self.connection and self.channel for normal usage
        '''

        try:
            self.connection = pika.BlockingConnection(
                MESSAGE_HOST
            )
        except ConnectionError as err:
            sys.stderr.write('ERROR: %sn' % str(err))
            print("Could not connect")

        #set up the internal variables
        self.queue = queue
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)

    def send_message(self, message):
        '''take the chan object, send message to it, and then close connection
            first 2 arguements should ideally be passed from start_Connection()
        '''
        self.channel.basic_publish(
            exchange='',
            routing_key='hello',
            body=message
        )
    def receive_message(self, callback):
        '''blockIO and wait for recieption of messages on queue'''
        def print_message(channel, method, properties, body):
            '''default case'''
            print("fetched '%s' from %s" % \
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
    #grab the first arguement or send something generic
    THING.send_message(' '.join(sys.argv[1:]) or "Generic Message")
    THING.receive_message('print')
    del THING
