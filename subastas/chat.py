# -*- coding: utf-8 -*-

"""
Chat Server
===========
This simple application uses WebSockets to run a primitive chat server.
"""

import os
import redis
import gevent
from flask import Flask, render_template
from flask_sockets import Sockets



import json
from collections import namedtuple

from Bid import Bid


from constants import REDIS_URL,REDIS_CHANNEL

app = Flask(__name__)
#app.debug = 'DEBUG' in os.environ
# log to stderr
import logging
from logging import StreamHandler
file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(file_handler)

sockets = Sockets(app)
myredis = redis.from_url(REDIS_URL)

from ChatBackend import ChatBackend
chats = ChatBackend(myredis,REDIS_CHANNEL,gevent,app)
chats.start()

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/viajes')
def viajes():
    return render_template('viajes.html')


@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    #while ws.socket is not None:
    while not ws.closed:
        # Sleep to prevent *contstant* context-switches.
        gevent.sleep()
        message = ws.receive()

        if message:
            app.logger.debug(u'Inserting message: {}'.format(message))
            bid_new = Bid(message)
            
            bid_last = myredis.lrange(bid_new.idprod, 0, 0)
            app.logger.debug(u'Last bid: {}'.format(bid_last))
            if bid_last:# prolly first time
                last_bid = Bid(bid_last[0])
                price_last = int(last_bid.bid)
            else:
                price_last = 0;

            #app.logger.debug('price: '+str(price_last))

            price_new = int(bid_new.bid)

            if price_new>price_last:
                myredis.lpush(bid_new.idprod,message)
                myredis.publish(REDIS_CHANNEL, message)
            else:
                error_msg = '{\"idprod\":'
                error_msg = error_msg+'\"'+bid_new.idprod+'\"'
                error_msg = error_msg+", \"userid\":"
                error_msg = error_msg+'\"'+bid_new.userid+'\"'
                error_msg = error_msg+", \"price_last\":"
                error_msg = error_msg+str(price_last)
                error_msg = error_msg+", \"bid\":-1 }"
                myredis.publish(REDIS_CHANNEL, error_msg)
            


@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via ChatBackend."""
    chats.register(ws)
    app.logger.debug('new user')
    #while ws.socket is not None:
    while not ws.closed:
        #print "receive2"
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()


