import argparse, sys
import socket

parser = argparse.ArgumentParser(description='Local Host Definition')
parser.add_argument('-host', '--HOST')
args = parser.parse_args()

if args.HOST is None:
    host = ''
else:
    host = args.HOST


class IRCClient:

    def __init__(self, server, username, port ):
        self.username = username
        self.server = server
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.connection.connect((self.server, self.port))
        except socket.error, msg:
            print "Error occurred during attempt to connect to:"
            print "{} at port {}".format(server, port)
            print "Error Message: {}".format(msg)
            print "Please restart the program"
            sys.exit(0)

    def send_comm(self, cmd, message):
        command = "{} {}\r\n".format(cmd, message)
        self.connection.send(command)

    def join_channel(self, channel):
        cmd="JOIN"
        self.send_comm(cmd, channel)

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
        if message.find('PING') != -1:
            cmd="PONG"
            self.send_comm(cmd, "")

    def disconnect(self):
        self.connection.close()

    def response(self):
        return self.connection.recv(2048)

    def print_response(self):
        resp = self.response()
        if resp:
            print resp
#            msg = resp.strip().split(" ")
#            print "\n {} {}".format(msg[1].split("!")[0], msg[2].strip())


if __name__ == "__main__":
    port = 6667
    user = "csherpa"
    channel = "general"

    cmd = ""
    client = IRCClient(host, user, port)
    client.connect()
    client.join_channel(channel)

    print "\n"
    while cmd != "quit()":
        client.heartbeat(cmd)
        cmd = raw_input("{}@{}: ".format(user, channel)).strip()

        if cmd == "quit()":
            client.send_comm("QUIT", "")
            exit(0)
        if cmd and len(cmd) > 0:
            client.send_message(cmd)

        client.print_response()

