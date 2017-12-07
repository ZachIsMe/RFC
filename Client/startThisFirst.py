import argparse
import sys
import socket
import select
import time

BUFFER = 1024
DEBUG = False

##ArgsParse from the command line for different setting
parser = argparse.ArgumentParser(description='Local Host Definition')
parser.add_argument('-ip', '-host', '--HOST', help="Host")
parser.add_argument('-p', '-port', '--PORT', help="Port Number")
parser.add_argument('-u', '-user', '--USER', help="Username")
parser.add_argument('--debug', action='store_true', help="Debug")
args = parser.parse_args()

if args.HOST is None: host = ''
else: host = args.HOST

if args.PORT is None: port = 6667
else: port = args.PORT

if args.USER is None: user = "Default"
else: user = args.USER

if args.debug: DEBUG = True


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
        if DEBUG:
            sys.stdout.write("To Server: {}".format(command))
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

    def list_members(self, roomname):
        cmd="LISTMEM"
        self.send_comm(cmd, roomname)

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
            #HEARTBEAT TRUNCATED
            if resp == "PING":
                cmd="PONG"
                self.send_comm(cmd, "")
            else:
                sys.stdout.write("From Server: {}".format(resp))
        elif not resp:
            '''Manpreet suggested this to validate server instead of heartbeat'''
            print "Server is down"
            sys.exit()

    def usage(self):
        print "\nCommand Syntax\n\tDescription"
        print "------------------------"
        for key, value in options.iteritems():
            print "{}\n\t{}".format(key, value)


#options dictionary
options = {"quit()": "Exiting the program",
           "join() <Room>": "Join <channel>",
           "join() <Room1> <Room2> <Room3>": "Join multiple <rooms>. Space delimited",
           "create() <RoomName>": "Create a room",
           "lr()": "List all rooms",
           "lm() <Room>": "List members in the current channel",
           #"sm() <Room>":"Send general message to <Room>",
           "le() <Room>": "Leave current <RoomName>",
           "smr() <Room1> <Room2> <Room3>: MESSAGE": "Send message to targeted rooms. Colon delimited for Message; "
                                                     "Space delimited for Rooms",
           "smr() <Room> : MESSAGE": "Send message to a specific room",
           "usage()": "Print out the usage for the client",
           }


def onearg(input, cmd):
    arr = input.rstrip('\n').strip().split("()")
    if len(arr) >= 2:
        if len(arr[1]) > 1:
            arg = arr[1].strip().split()[0]
        else:
            arg = arr
        return arg
    else:
        print "{} needs at least 1 arg".format(cmd)
        return ""


def multijoin(input, key):
    if input is None:
        return
    elif input.startswith(key):
        a = input.strip().split("()")
        b = a[1].split()
        for idx, val in enumerate(b):
            print "JOIN {}".format(val)


def multiroommsg(input, key):
    if input is None:
        return "Invalid Input:", "NoGoPie"
    elif input.startswith(key):
        if key.strip() == "smr()":
            a = input.split(key)[1].strip()
            b = a.split(":")[1].strip()
            c = a.split(":")[0].strip()
            d = c.split()
        return d, b
    else:
        return "Invalid Input:", "NoGoPie"


#Main
if __name__ == "__main__":
    channel = "general"

#ask for username
    cmd = ""
    client = IRCClient(host, user, port)

    client.connect_to_server()
    time.sleep(1)
    client.create_room("general")

    stuff = [sys.stdin, client.connection]

    sys.stdout.write("\n{}@: ".format(user))
    while 1:
        something, y, z = select.select(stuff, [], [])
        for s in something:
            if s is client.connection:
                sys.stdout.write("\n")
                client.servermsg_display()
                sys.stdout.write("\n{}@: ".format(user))
            elif s is sys.stdin:
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
                    arg = onearg(input, "lm()")
                    if DEBUG: print arg
                    client.list_members(arg)
                #JOIN ROOM BELOW
                elif input.startswith("join()"):
                    key = "join()"
                    if input is None:
                        continue
                    elif input.startswith(key):
                        cmd = input.strip().split("()")
                        rooms = cmd[1].split()
                        if DEBUG: print cmd,rooms
                        for idx, val in enumerate(rooms):
                            time.sleep(1)
                            client.join_room(val)
                #CREATE ROOM BELOW
                elif input.startswith("create()"):
                    arg = onearg(input, "create()")
                    if DEBUG: print arg
                    client.create_room(arg)
                #SEND MESSAGE TO SPECIFIC ROOM BELOW
                elif input.startswith("smr()"):
                    ### MESSAGE TO ONE ROOM
                    key = "smr()"
                    chan, msg = multiroommsg(input, key)
                    if 'NoGoPie' in msg:
                        if DEBUG: print "Invalid Message"
                        continue
                    else:
                        for idx, val in enumerate(chan):
                            time.sleep(1)
                            client.send_message_to_room(val, msg)
                #LEAVE ROOM
                elif input.startswith("le()"):
                    arr = input.rstrip('\n').strip().split("()")
                    if len(arr) >= 2:
                        try:
                            arg = None
                            if len(arr[1]) > 1:
                                arg = arr[1].strip().split()[0]
                            else:
                                arg = arr
                            client.leave_room(arg)
                        except ValueError:
                            client.usage()
                    else:
                        print "{} needs at least 1 args".format("le()")
                #COMMAND USAGE INFORMATION
                elif input.startswith("usage()"):
                    client.usage()
                elif input and len(input) > 0:
                    client.usage()

