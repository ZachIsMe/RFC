from SimpleHTTPServer import SimpleHTTPRequestHandler
import sys
import socket
import os
import signal
import shutil
import select

host = '127.0.0.1'
# could instead pass in '' in bind tuple
port = 50000
backlog = 5
size = 1024

# server/socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((host, port))  # passing tuple as single argument

# accept call from client
server.listen(5)  # max one queued connection. Min 0
reload(sys)
# sys.setdefaultencoding("UTF8")  # unnecessary


def connect(self):
    self.sockets = []
    input = [server, sys.stdin]
    running = 1
    while running:
        try:
            inputready, outputready, exceptready = select.select(input, [], [])
        except select.error, e:
            print "select error\n"
            break
        for s in inputready:
            if s == server:
                client, address = server.accept()
                client_name = "PLACEHOLDER CLIENT NAME"
                print "Hello " + client_name
                input.append(client)
            elif s == sys.stdin:
                junk = sys.stdin.readline()
                if junk == "DISCONNECT":
                    print "Closing server"
                    for ss in self.sockets:
                        ss.close()
                    self.server.close()
                else:
                    running = 0  # May need to place with if statement, OR sets all all times within elif
            else:
                data = s.recv(size)
                if data:
                    s.send(data)
                else:
                    s.close()
                    input.remove(s)
    server.close()


#  def create_room(cname, client):

class Chat:
    def __init__(self):
        self.rooms = {}

    def list_rooms(self, client):
        if len(self.rooms) == 0:
            message = "There are no rooms available\n"
            client.socket.sendall(message.encode())
        else:
            for r in self.rooms:
                print(self.rooms[r].client)


class Room:
    def __init__(self, name):  # Default constructor
        self.name = name  # Change later to pass in name from client in class declaration
        self.sockets = []
        self.memebers = []  # Holds the names of users who are in the chat room

    def client_joined(self, a_client):
        welcome_message = "Hello, " + a_client.name + "! Welcome to Room " + self.name + "!"
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

 # Helpful:
'''
def create_channel(channelname, client, socket, channelMap):
    if check_channel_exist(channelname, channelMap) == False:
        channelMap[channelname] = [[client,socket]]
        msg = "Room %s Created" % (channelname)
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(socket,new_message)
        return channelMap
    else:
        msg = "Room is Existing....Joining Room"
        new_message = '\n[' + 'SERVER@6510' + ']>> ' + msg
        send(socket, new_message)
        join_channel(channelname, client, socket, channelMap)
'''

'''
# CURRENTLY UNUSED CODE

# initialization total
IT = ''

# initialize client socket
csock = []

# number of clients
numc = 2



# accept from client
for i in range(numc):
    (client, ap) = server.accept()
    client.setblocking(0)  # non-blocking if set to 0
    csock.append(client)

# loop, accepting from anyone
while(len(csock) > 0):
    client = csock.pop(0)
    csock.append(client)
    try:
        check = client.recv(1)
        if check =='':
            client.close()
            csock.remove(client)
        IT += check
        client.send(IT)
    except: pass

server.close()
print 'Initialization Total is ', IT


def shutdown(self):
    os.kill(self.child_pid, signal.SIGTERM)
    os.waitpid(self.child_pid, 0)
    if self.state_dir:
        try:
            shutil.rmtree(self.state_dir)
        except IOError:
            pass

'''
'''def disconnect(clientList)
    for c in clientList
        if'''
