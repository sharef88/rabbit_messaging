#!/usr/bin/python3
'''Module for building a pika-amqp connection'''
import ssl
import json
import pika
__author__ = "sharef88"

class Messaging(object):
    ''' Class for setting up an AMQP Connection
    '''
    @staticmethod
    def _parse_ssl(config_input):
        config_input['cert_reqs'] = ssl.CERT_REQUIRED
        config_input['ssl_version'] = ssl.PROTOCOL_TLSv1_2
        return config_input

    def _open_config(self):
        ''' open the config.json file that is in the same directory and de-serialize its contents.
        '''
        with open("config.json", 'r') as fin:
            config = json.load(fin)['rabbit']
            #convert credentials into pika credentials
            config['credentials'] = pika.PlainCredentials(**config['credentials'])
            #add some extras to the ssl options
            config['ssl_options'] = self._parse_ssl(config['ssl_options'])
            return config

    def __init__(self, exchange, routing, exclusive=False):
        ''' This function will configure self.connection and self.channel for normal usage
        '''
        #Create the connection using data from the config file
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(**self._open_config()))

        #set up the internal variables
        self.routing = routing
        self.channel = self.connection.channel()
        self.exchange_name = exchange
        self.exchange = self.channel.exchange_declare(
            exchange=exchange,
            exchange_type='topic'
            )
        if not exclusive:
            self.queue = self.channel.queue_declare(queue=self.routing)
        else:
            self.queue = self.channel.queue_declare(exclusive=True)

        self.channel.queue_bind(
            exchange=exchange,
            queue=self.queue.method.queue,
            routing_key=routing
            )



    def send_message(self, message, key):
        '''
        Send message to self.channel,
        will always json-serialize the message to best facilitate reception of the message
        '''

        #serialize the message into json
        message = json.dumps(message)
        #publish the message to the queue "routing key" via "exchange"
        #this is largely amqp/rabbit naming convention
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=key,
            body=message
        )
    def receive_message(self, callback, loop):
        '''
        Receive Messages:
        Wrapper around the callback function.
            Turns the callback into a generator over the queue itself.

        loop the reception while:
        -- loop == -1 -> loop infinitely
        -- loop == 0 -> loop until queue is empty
        -- loop == n -> loop until received n messages
        '''
        #convert a loop statement to timeout
        if loop == 0:
            timeout = 5 #if loop until empty then set a timeout to grab the "empty" state
        else:
            timeout = None
        self.channel.basic_qos(prefetch_count=2)
        #Try: statement is for catching the Nonetype not iterable error that this would cause
        sent_messages = 0
        try:
            for method, header, body in self.channel.consume(
                    queue=self.queue.method.queue,
                    inactivity_timeout=timeout,
                ):

                sent_messages = method.delivery_tag           #Make sure you record the thing-doing!
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
                #do the thing, you know, the thing!
                yield callback(self.channel, method, header, body)

                #kill the loop 'pon conditions stated above
                if loop == method.delivery_tag:
                    break
        except TypeError:
            #raise err
            pass
        #return a report of sent messages
        requeued = self.channel.cancel()
        self.channel.close()
        return {
            'sent': sent_messages,
            'requeued': requeued,
            }
    def __del__(self):
        self.close()

    def close(self):
        '''
        cleanup, what else?
        '''
        try:
            self.connection.close()
        except (AttributeError, pika.exceptions.ConnectionClosed):
            pass
