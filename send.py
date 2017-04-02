#!/usr/bin/python3.4
#import sys
import pika
__author__ = "sharef88"

MESSAGE_HOST = pika.ConnectionParameters(
    '192.168.1.155',
    5672,
    '/',
    pika.PlainCredentials(
        "guest",
        "guest"
    )
)


def start_Connection(queue):
    ''' This function will return a pika.BlockingConnection.channel object
    '''

    connection = pika.BlockingConnection(
        MESSAGE_HOST
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue)
    return connection, channel

def send_message(conn, chan, message):
    '''take the chan object, send message to it, and then close connection
        first 2 arguements should ideally be passed from start_Connection()
    '''
    #sys.argv[0] is the program name itself, so we need to grab everything else and send it as a msg
    #message = ' '.join(sys.argv[1:]) or "Hello World!"
    chan.basic_publish(
        exchange='',
        routing_key='hello',
        body=message
    )
    conn.close()
    return
send_message(*start_Connection("hello"), "greetings")
