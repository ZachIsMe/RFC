import sys
import socket
import string
import argparse
import logging


class irc_client():

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

    #Objective #6
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

    #Objective #10
    def sendmsg(self, msg, channel):
        self.irc.send(("PRIVMSG "+ channel +" :"+msg+"\n").encode("UTF-8"))

    def ping(self):
        self.irc.send(("PONG :pingis\n").encode("UTF-8"))

#    def createChannel(self, name, channel):
#    def listRooms(self):
#    def joinRoom(self, channel, name):
#    def leaveRoom(self, channel, name):
#    def listMembersInChan(self, channel):

    #Objective #13
#    def disconnect(self):


    #Objective 16
#    def Heartbeat(self):


