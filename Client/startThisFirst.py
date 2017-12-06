import argparse, sys
import socket
import select
import time

parser = argparse.ArgumentParser(description='Local Host Definition')
parser.add_argument('-host', '--HOST')
args = parser.parse_args()

if args.HOST is None:
    host = ''
else:
    host = args.HOST

BUFFER = 1024

#Class IRCClient modifed from https://raw.githubusercontent.com/bl4de/irc-client/master/irc_client.py
class IRCClient:

    def __init__(self, server, username, port):
        self.username = username
        self.server = server
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.connection.connect((self.server, self.port))
            self.send_comm("USERNAME", self.username)
        except socket.error, msg:
            print "Error occurred during attempt to connect_to_server to:"
            print "{} at port {}".format(self.server, self.port)
            print "Error Message: {}".format(msg)
            print "Please restart the program and the server"
            sys.exit(0)

    def send_comm(self, cmd, message):
        command = "{} {}\n".format(cmd, message)
        print "To Server: {}".format(command)
        self.connection.send(command)

    def join_room(self, channel):
        cmd="JOIN"
        self.send_comm(cmd, channel)

    def leave_room(self, channel):
        cmd="LEAVE"
        self.send_comm(cmd, channel)

    def change_channel(self, fromChan, toChan ):
        try:
            print "Leaving {}".format(fromChan)
            self.leave_room(fromChan)
        except socket.error:
            print "Could not leave {}".format(fromChan)
        try:
            print "Joining {}".format(toChan)
            self.join_room(toChan)
        except socket.error:
            print "Could not join {}".format(toChan)

    def list_rooms(self):
        cmd="LISTROOM"
        self.send_comm(cmd, "")

    def list_members(self):
        cmd="LISTMEM"
        self.send_comm(cmd, "")

    def create_room(self, roomname):
        cmd="CREATE"
        self.send_comm(cmd, roomname)

    def send_all(self, message):
        cmd="SENDALL"
        self.send_comm(cmd, message)

    def send_message_to_room(self, channel, message):
        cmd="{} {}".format("MESSAGE", channel)
        self.send_comm(cmd, message)

    def heartbeat(self, message):
        if message.startswith("PING"):
            cmd="PONG"
            self.send_comm(cmd, "")

    def disconnect(self):
        self.connection.close()

    def response(self):
        return self.connection.recv(BUFFER)

    def servermsg_display(self):
        resp = self.response()
        if resp:
            if resp == "PING":
                cmd="PONG"
                self.send_comm(cmd, "")
            else:
                print "From Server: {}".format(resp)
        elif not resp:
            '''Manpreet suggested this to validate server instead of heartbeat'''
            print "Server is down"
            sys.exit()

    def usage(self):
        print "Command\t\tDescription"
        for key, value in options.iteritems():
            print "{}\t\t{}".format(key, value)


#options dictionary
options = {"quit()": "Exiting the program",
           "join() <Channel>": "Join <channel>",
           "create() <RoomName>": "Create a room",
           "lr()": "List all rooms",
           "lm() <RoomName>": "List members in the current channel",
           #"sm() <Room>":"Send general message to <Room>",
           "le() <RoomName>": "Leave the current room. Fails if you're the lobby",
           "sma()": "Send message to all rooms",
           "smr() <RoomName> MESSAGE": "Send message to a specific room",
           "usage()": "Print out the usage for the client",
           }

#Main
if __name__ == "__main__":
    port = 6667
    user = "csherpa"
    channel = "general"

#ask for username
    cmd = ""
    client = IRCClient(host, user, port)

    client.connect_to_server()
    time.sleep(1)
    client.create_room("general")


    stuff = [sys.stdin, client.connection]

    while 1:
        print "{}@{}: ".format(user, channel)
#        sys.stdout.flush()
        something, y, z = select.select(stuff, [], [])
        for s in something:
            if s is client.connection:
                #client.heartbeat(s)
                client.servermsg_display()
            elif s is sys.stdin:
                #print "{}@{}: ".format(user, channel)
                sys.stdout.flush()
                input = sys.stdin.readline()
                if input.startswith("quit()"):
                    client.send_comm("DISCONNECT", "")
                    client.disconnect()
                    sys.exit(0)
                #LIST MEMBERS BELOW
                elif input.startswith("lr()"):
                    client.list_rooms()
                #LIST MEMBERS BELOW
                elif input.startswith("lm()"):
                    input = input.split("()")[1].strip().split()[0]
                    client.list_members()
                #JOIN ROOM BELOW
                elif input.startswith("join()"):
                    chan = input.split("()")[1].strip().split()[0]
                    client.join_room(chan)
                #CREATE ROOM BELOW
                elif input.startswith("create()"):
                    chan = input.split("()")[1].strip().split()[0]
                    client.create_room(room)
                #SEND MESSAGE TO SPECIFIC ROOM BELOW
                elif input.startswith("smr()"):
                    chan = input.split("()")[1].strip().split(" ", 1)[0]
                    msg = input.split("()")[1].strip().split(" ", 1)[1]
                    client.send_message_to_room(chan, msg)
                #SEND MESSAGE TO SERVER BELOW
                elif input.startswith("sma()"):
                    chan = "ALL"
                    msg = input.split("()")[1].split(" ", 1)[1]
                    client.send_message_to_room(chan, msg)
                #LEAVE ROOM
                elif input.startswith("le()"):
                    room = input.split("()")[1].strip().split()
                    client.leave_room(room)
                #COMMAND USAGE INFORMATION
                elif input.startswith("usage()"):
                    client.usage()
                elif input and len(input) > 0:
                    client.send_message_to_room(channel, input)

