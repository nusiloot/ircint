#!/usr/bin/python3
#-*- coding: utf-8 -*-
# 
enc = "utf-8"

appname = "ircint"

database = "ircint.db"

server = "irc.malwaretech.com"
#server = "irc.hackint.org"
port   = 6667

connectionlist = {"irc.malwaretech.com":[6667,["#MalwareTech"]]}


nick   = "randomdood1337"
#channellist = ["#testering"]
channellist = ["#MalwareTech"]

def main():
    print("This file shouldn't be run directly. It contains the settings for %s" %  appname)
    pass

if __name__ == "__main__":
    main()

