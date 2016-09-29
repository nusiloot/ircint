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
#import requests

from jaraco.stream import buffer

def on_welcome(connection, event):
    for target in settings.channellist:
        if irc.is_channel(target):
            connection.join(target)
            out.promptOK("Connected to channel %s" % target)

def on_join(connection, event):
    pass

def on_disconnect(connection, event):
    raise SystemExit()

def on_privmsg(connection, event):
    out.promptInfo("Privmsg received!")
    log(event)

def on_pubmsg(connection, event):
    out.promptInfo("Pubmsg received!")
    log(event)

def log(event):
    global uniqid
    global link_id
    global db
    global cur
    msgtype = event.type
    timestamp = str(datetime.datetime.now()).split('.')[0]
    source = event.source
    nick = source.nick
    channel = event.target
    message = event.arguments[0]
    hash = hashlib.md5(bytes(message, enc)).hexdigest()
    print(msgtype, timestamp, source, nick, channel, message, hash)
    cur.execute("""INSERT INTO messages(id, msgtype, timestamp, source, nick, channel, message, hash) VALUES (?,?,?,?,?,?,?,?);""", (uniqid, msgtype, timestamp, source, nick, channel, message, hash))
    for link in get_links(message):
        cur.execute("""INSERT INTO links(id, messageid, link) VALUES (?,?,?);""", (link_id, uniqid, link))
        link_id += 1
    uniqid += 1
    db.commit()


def get_links(message):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
    return urls


def main():
    reactor = irc.Reactor()
    global out
    out = output.Output()
    global db
    db  = sqlite3.connect(settings.database)
    global cur
    cur = db.cursor()
    cur.execute("SELECT max(id) FROM messages")
    global uniqid
    uniqid = cur.fetchall()[0][0]+1 or 0 # TODO test
    cur.execute("SELECT max(id) FROM links")
    global link_id
    link_id = cur.fetchall()[0][0]+1 or 0 # TODO test
    
    try:
        out.promptInfo("Trying to connect to %s on port %s" % (settings.server, str(settings.port)) )
        x = reactor.server()
        x.buffer_class = buffer.LenientDecodingLineBuffer
        c = x.connect(settings.server, settings.port, settings.nick)

    except irc.ServerConnectionError:
        out.promptFail(sys.exc_info()[1])
        raise SystemExit(1)

    c.add_global_handler("welcome",on_welcome)
    c.add_global_handler("join",on_join)
    c.add_global_handler("disconnect",on_disconnect)
    c.add_global_handler("privmsg",on_privmsg)
    c.add_global_handler("pubmsg",on_pubmsg)
    #c.add_global_handler("",)

    out.promptOK("Initiation done. Starting to listen...")

    try:
        reactor.process_forever()
    except KeyboardInterrupt:
        raise SystemExit()


if __name__ == "__main__":
    main()

