import argparse, sys
import socket
import select

parser = argparse.ArgumentParser(description='Local Host Definition')
parser.add_argument('-host', '--HOST')
args = parser.parse_args()

if args.HOST is None:
    host = ''
else:
    host = args.HOST

BUFFER = 1024

class IRCClient:

    def __init__(self, server, username, port):
        self.username = username
        self.server = server
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.connection.connect((self.server, self.port))
            self.send_comm("USERNAME", self.username)
        except socket.error, msg:
            print "Error occurred during attempt to connect to:"
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

    def send_message_to_room(self, message, channel):
        cmd="{} {}".format("SENDMSG", channel)
        self.send_comm(cmd, message)

    def send_message(self, message):
        cmd="MESSAGE"
        self.send_comm(cmd, message)

    def heartbeat(self, message):
        if message.startswith("PING"):
            cmd="PONG"
            self.send_comm(cmd, "")

    def disconnect(self):
        self.connection.close()

    def response(self):
        return self.connection.recv(BUFFER)

    def print_response(self):
        resp = self.response()
        if resp:
            if resp == "PING":
                cmd="PONG"
                self.send_comm(cmd, "")
            else:
                print "From Server: {}".format(resp)
        elif not resp:
            print "Server is down"
            sys.exit()

    def usage(self):
        print "USAGE"
        print "Command\t\tDescription"
        for key, value in options.iteritems():
            print "{}\t\t{}".format(key, value)


#            msg = resp.strip().split(" ")
#            print "\n {} {}".format(msg[1].split("!")[0], msg[2].strip())

#options dictionary
options={"quit()":"Exiting the program",
         "join() <channel>":"Join <channel>",
         "lr()":"List all rooms",
         "lm()":"List members in the current channel",
#         "sm() <Room>":"Send general message to <Room>",
         "le()":"Leave the current room. Fails if you're the lobby",
         "sma()":"Send message to all rooms",
         "usage()":"Print out the usage for the client",
         }

#Main
if __name__ == "__main__":
    port = 6668
    user = "csherpa"
    channel = "general"

    cmd = ""
    client = IRCClient(host, user, port)
    client.connect()
    client.join_room(channel)

    stuff = [sys.stdin, client.connection]

    while 1:
        print "{}@{}: ".format(user, channel)
#        sys.stdout.flush()
        something, y, z = select.select(stuff, [], [])
        for s in something:
            if s is client.connection:
                #client.heartbeat(s)
                client.print_response()
            elif s is sys.stdin:
                #print "{}@{}: ".format(user, channel)
                sys.stdout.flush()
                input = sys.stdin.readline()
                if input.startswith("quit()"):
                    client.send_comm("QUIT", "")
                    client.disconnect()
                    sys.exit(0)
                elif input.startswith("lr()"):
                    client.list_rooms()
                elif input.startswith("lm()"):
                    client.list_members()
                elif input.startswith("join()"):
                    chan = input.split("()")
                    #if len(chan) > 1:
                    #    print chan
                    client.join_room(chan[1].strip())
                elif input.startswith("smr()"):
                    room = input
                    client.send_message_to_room(room, channel)
                elif input.startswith("sma()"):
                    message = input
                    client.send_message_to_room(message, "ALL")
                elif input.startswith("le()"):
                    room = input
                    client.leave_room(room)
                elif input.startswith("usage()"):
                    client.usage()
                elif input and len(input) > 0:
                    client.send_message(input)

#        client.print_response()

