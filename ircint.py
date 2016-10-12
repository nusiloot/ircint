#!/usr/bin/python3
#-*- coding: utf-8 -*-
# 
enc = "utf-8"

import settings
import output

import irc.client as irc
#import argparse

import sqlite3
import sys
import datetime
import re
import hashlib
import threading
import queue
#import requests

from jaraco.stream import buffer



class Client(irc.SimpleIRCClient):
    def __init__(self, channellist, servername, queue): # TODO target?
        irc.SimpleIRCClient.__init__(self)
        self.channellist = channellist
        self.q = queue
        self.servername = servername
        self.connection.buffer_class = buffer.LenientDecodingLineBuffer

    def on_welcome(self, connection, event):
        for target in self.channellist:
            if irc.is_channel(target):
                connection.join(target)
                out.promptOK("Connected to channel %s" % target)

    def on_join(self, connection, event):
        pass

    def on_disconnect(self, connection, event):
        raise SystemExit()

    def on_privmsg(self, connection, event):
        #out.promptInfo("Privmsg received!")
        self.q.put([event,self.servername])
        #self.logger.log(event, self.servername)

    def on_pubmsg(self, connection, event):
        #out.promptInfo("Pubmsg received!")
        self.q.put([event,self.servername])
        #self.logger.log(event, self.servername)

class Logger():
    def __init__(self, dbfile):
        self.db = sqlite3.connect(dbfile)
        self.cur = self.db.cursor()
        self.cur.execute("SELECT max(id) FROM messages")
        self.uniqid = self.cur.fetchall()[0][0]+1 or 0 # TODO test
        self.cur.execute("SELECT max(id) FROM links")
        self.link_id = self.cur.fetchall()[0][0]+1 or 0 # TODO test

    def log(self, event, servername):
        msgtype = event.type
        timestamp = str(datetime.datetime.now()).split('.')[0]
        source = event.source
        nick = source.nick
        channel = event.target
        message = event.arguments[0]
        hash = hashlib.md5(bytes(message, enc)).hexdigest()
        self.cur.execute("""INSERT INTO messages(id, msgtype, timestamp, source, nick, channel, message, hash, server) VALUES (?,?,?,?,?,?,?,?,?);""", (self.uniqid, msgtype, timestamp, source, nick, channel, message, hash, servername))

        for link in self.get_links(message):
            self.cur.execute("""INSERT INTO links(id, messageid, link) VALUES (?,?,?);""", (self.link_id, self.uniqid, link))
            self.link_id += 1
        self.uniqid += 1
        self.db.commit()


    def get_links(self, message):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        return urls

class LoggerWorker(threading.Thread):
    def __init__(self, dbfile):
        threading.Thread.__init__(self)
        self.dbfile = dbfile
    def run(self):
        self.logger = Logger(self.dbfile)
        while True:
            item = q.get()
            if item is None:
                continue
            self.logger.log(item[0],item[1])
            q.task_done()
        pass


class ClientThreadWrapper(threading.Thread):
    def __init__(self, threadID, channellist, servername, q, port, nick):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.servername = servername
        try:
            out.promptInfo("Trying to connect to %s on port %s" % (self.servername, str(port)))
            self.client = Client(channellist, self.servername, q)
            self.client.connect(self.servername, port, nick)
        except irc.ServerConnectionError:
            out.promptFail(sys.exc_info()[1])
            raise SystemExit(1)
    def run(self):
        out.promptInfo("Starting Client for %s"% self.servername)
        self.client.start()

def main():
    global out
    out = output.Output()
    
    global q

    q = queue.Queue() 
    #logger = Logger(settings.database)
    l = LoggerWorker(settings.database)
    for con in settings.connectionlist:
        name = con
        port = settings.connectionlist[con][0]
        chans = settings.connectionlist[con][1]
        try:
            x = ClientThreadWrapper(0, chans, name, q, port, settings.nick)
            x.start()
        except irc.ServerConnectionError:
            out.promptFail(sys.exc_info()[1])
            raise SystemExit(1)

    l.start()
    out.promptOK("Initiation done. Starting to listen...")


    
    """
    logger = Logger(settings.database)
    for con in settings.connectionlist:
        name = con
        port = settings.connectionlist[con][0]
        chans = settings.connectionlist[con][1]
        try:
            out.promptInfo("Trying to connect to %s on port %s" % (name, str(port)) )
            c = Client(chans, name, logger)
            c.buffer_class = buffer.LenientDecodingLineBuffer
            c.connect(name, port, settings.nick)
        except irc.ServerConnectionError:
            out.promptFail(sys.exc_info()[1])
            raise SystemExit(1)
        c.start()

    out.promptOK("Initiation done. Starting to listen...")

    try:
        reactor.process_forever()
    except KeyboardInterrupt:
        raise SystemExit()
    """

if __name__ == "__main__":
    main()

