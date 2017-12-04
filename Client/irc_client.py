import sys
import socket
import threading
import string
import argparse
import logging
import re



class IRCClient:

    irc = socket.socket()

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def join_channel(self, channel, name):
        self.irc.send(("JOIN %s\r\n" % channel).encode())
        print("Joined %s as %s\n" % (channel, name))
        ircmsg=""
        while ircmsg.find("End of /NAMES list.") == -1:
            ircmsg = ircmsg.recv(2048).decode("UTF-8")
            ircmsg = ircmsg.strip('\n\r')
            print (ircmsg)

    # Objective #6
    def connect(self, host, port, channel, name, log):
        try:
            self.irc.connect((host, port))
            print("Connect to %s\n" % host)
            self.irc.send(("NICKNAME %s\r\n" % name).encode("UTF-8"))
            self.irc.send(("USER %s %s: %s\r\n" % (name,name,name)).encode("UTF-8"))
            self.irc.send(("JOIN %s\r\n" % channel).encode("UTF-8"))
            print("Joined %s as %s\n" % (channel, name))
        except Exception as e:
            print (e)
            sys.exit(1)

    def send(self, channel, message):
        self.irc.send("PRIVMSG " + channel + " " + message +"n")

    # Objective #10
    def sendmsg(self, msg, channel):
        self.irc.send(("PRIVMSG "+ channel +" :"+msg+"\n").encode("UTF-8"))

    def ping(self):
        self.irc.send(("PONG :pingis\n").encode("UTF-8"))

    def choices(message, sclient, self):
        command = message.split()[0]
        count = len(re.findall(r'\w+',message))
        if command == "CREATE":
            if count !=2:
                output = "Invalid: input CREATE roomname"
                # send to client
            else:
                sender = "temp"
                # create channel
        elif command == "DISCONNECT":
            if count!=2:
                output = "Invalid: input DISCONNECT roomname"

            else:
                sender = "temp"

        elif command == "JOIN":
            if count == 2:
                sender = "temp"
                # join channel
            else:
                output = "Invalid: please input at least one room/channel to join"
        elif command == "LIST":
            if count > 1:
                output = "Invalid: only input LIST"

            elif count == 1:
                room_list = []
                # list rooms


#    def createChannel(self, name, channel):
#    def listRooms(self):
#    def joinRoom(self, channel, name):
#    def leaveRoom(self, channel, name):
#    def listMembersInChan(self, channel):

    # Objective #13
#    def disconnect(self):


    # Objective 16
#    def Heartbeat(self):

