import argparse, sys
import socket

parser = argparse.ArgumentParser(description='Local Host Definition')
parser.add_argument('-host', '--HOST')
args = parser.parse_args()

if( args.HOST == None ):
  host = ''
else:
  host = args.HOST

port = 6667
user = None
channel = None


#connect
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Host " + host + "\n"
s.connect((host, port))
print "Connected to server\n"

#socket_list = [ sys.stdin, s ]
#send message
joined=False

cmd=None
while (joined == False ):
    init=s.conn.recv(512) #To check if we're connected
    print init.strip()

    #Heartbeat response to server
    if "PING" in init:
        s.send("PONG", ":"+ init.split(":")[1])

while( cmd != '/quit'):
    cmd = raw_input("< {}> ".format(user)).strip()
    if cmd == "/quit":
        s.send("QUIT")
        exit(0)
    if cmd and len(cmd) > 0:
        s.send("PRIVMSG " + channel + " " + cmd + "n")
        #do stuff

       # target=s.conn.recv(512)))
'''
    ircmsg = s.recv(1024)

    if ircmsg.find('PING') != -1:
        s.send('PONG ' + ircmsg.split() [1] + 'rn')
    print ircmsg
'''
