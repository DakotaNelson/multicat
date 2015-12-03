#! /usr/bin/env python

import os
import sys
import string
import random
from time import sleep

from comms import Comms

from params import *

class CncComms(Comms):
    def __init__(self, channel, encoders, channelParams, encoderParams):
        super(CncComms, self).__init__(channel, encoders, channelParams, encoderParams)

    def sendJob(self, uid, jobName, cmdString):

        jobId = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(20)])

        self.send("{}:job:{}:{}:{}".format(uid, jobId, jobName, cmdString))


if __name__ == "__main__":
    comms = CncComms(channel, encoders, channelParams, encoderParams)
    try:
        while True:
            uid = raw_input("Enter a UID to send a command to: ")
            jobName = raw_input("Enter the job name: ")
            cmdText = raw_input("Enter the parameters to send: ")

            comms.sendJob(uid, jobName, cmdText)

    except KeyboardInterrupt:
        pass
