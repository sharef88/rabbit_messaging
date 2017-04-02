#!/usr/bin/python3.4
import sys
import pika
__author__ = "sharef88"

MESSAGE_HOST = pika.ConnectionParameters(
    '192.168.1.155',
    5672,
    '/',
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

    def __del__(self):
        try:
            self.connection.close()
        except AttributeError:
            sys.stderr.write("connection didn't exist, nothing to do")
            



if __name__ == '__main__':
    THING = Messaging("hello")
    THING.send_message("objected!")
    del THING
