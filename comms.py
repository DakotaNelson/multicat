#! /usr/bin/env python

import os
import sys
import string
import random

# put sneaky-creeper on the path, then import it
basePath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basePath, 'sneaky-creeper'))
from sneakers import Exfil


class Comms(object):
    """ Encapsulates all of the methods and data needed to communicate
        with the outside world """

    def __init__(self, channel, encoders, channelParams, encoderParams):
        self.channel = channel
        self.encoders = encoders
        self.channelParams = channelParams
        self.encoderParams = encoderParams

        # this sets a self.feed attribute
        self.setUpFeed()

    def setUpFeed(self):
        """ Set up the sneaky-creeper comms channel object """

        feed = Exfil(self.channel, self.encoders)
        feed.set_channel_params(self.channelParams)
        for enc, params in self.encoderParams.items():
            feed.set_encoder_params(enc, params)

        self.feed = feed

    def receive(self):
        """ Retrieve messages from the comms feed and return them all """
        msgs = self.feed.receive()
        return msgs

    def send(self, msg):
        """ Sends a message """
        self.feed.send(msg)
