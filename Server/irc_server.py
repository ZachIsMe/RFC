from SimpleHTTPServer import SimpleHTTPRequestHandler
import sys
import socket
import os
import signal
import shutil
import select
import re

#'127.0.0.1'
host = ''
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


class ServerMain:
    def __init__(self, port):
        self.sockets = 0
        self.cList = []
        # Socket List
        self.sockets = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(5)  # Max backlog value
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        print "Exiting"
        for s in socket:
            s.close()
            self.server.close()
            sys.exit(0)


    def connect(self):
        self.sockets = {}
        self.sockets[self.server] = "SuperServer"
        self.room_list = []
        # input = [self.server, sys.stdin]
        running = 1
        # cList = {'Global': []}  # Dictionary
        while running:
            try:
                inputready, temp1, temp2 = select.select(self.sockets.keys(), [], [])
            except select.error, e:
                print "select error\n"
                break
            for s in inputready:
                print "In for loop"
                if s == self.server:
                    print "Waiting for client"
                    client, address = self.server.accept()
                    print "Accepted client"
                    self.sockets[client] = client  # automatically adds key

                else:
                    data = s.recv(size)
                    if data:
                        # s.send(data)
                        # Room.choices(data, s, cList)
                        #parse here
                        print data
                        command = data.split()[0]
                        print "Command: " + command
                        print data.split()
                        count = len(data.split())
                        print count
                        if command == "USERNAME":
                            if count != 2:
                                output = "Invalid: input USERNAME name"
                                s.send(output)
                            else:
                                client_name = data.split()[1]
                                self.sockets[s] = client_name
                        elif command == "CREATE":
                            if count != 2:
                                output = "Invalid: input CREATE roomname"
                                # send to client
                                s.send(output)
                            else:
                                is_room = False
                                for c in self.room_list:
                                    if c.name == data.split()[1]:
                                        is_room = True
                                if is_room == False:
                                    output = "Creating room..."
                                    new_room = Channel(data.split()[1])
                                    s.send(output)
                                    output = "Joining room..."
                                    new_room.add_client(self.sockets[s], s)
                                    self.room_list.append(new_room)
                                    s.send(output)
                                    # create channel
                                if is_room == True:
                                    output = "Room already exists. Joining now..."
                                    s.send(output)
                                    for c in self.room_list:
                                        if c.name == data.split()[1]:
                                            output = "Joining room..."
                                            s.send(output)
                                            c.add_client(self.sockets[s], s)

                        elif command == "LEAVE":
                            if count != 2:
                                output = "Invalid: input LEAVE roomname"
                                s.send(output)
                            else:
                                output = "Leaving"
                                s.send(output)
                                for c in self.room_list:
                                    print c.name
                                    if c.name == data.split()[1]:
                                        c.remove_client(c.name)
                                        break

                        elif command == "DISCONNECT":
                            if count != 1:
                                output = "Invalid: input DISCONNECT"
                                s.send(output)
                            else:
                                for c in self.room_list:
                                    c.check_client(self.sockets[s])
                                del self.sockets[s]
                                s.close()


                        elif command == "JOIN":
                            if count == 2:
                                for c in self.room_list:
                                    if c.name == data.split()[1]:
                                        output = "Joining channel..."
                                        s.send(output)
                                        c.add_client(self.sockets[s], s)
                                    else:
                                        output = "No channel to join matching that name"
                                        s.send(output)
                                # join channel
                            else:
                                output = "Invalid: please input at least one room/channel to join"
                                s.send(output)
                        elif command == "LISTROOM":
                            if count != 1:
                                output = "Invalid: only input LISTROOM"
                                s.send(output)
                            else:
                                for c in self.room_list:
                                    output = c.name
                                    s.send(output)

                        elif command == "LISTMEMBERS":
                            if count != 1:
                                output = "Invalid: input LISTMEMBERS roomname"
                                s.send(output)
                            else:
                                for c in self.room_list:
                                    if c.name == data.split()[1]:
                                        mem_list = c.member_list()
                                        for i in mem_list:
                                            s.send(i)
                        elif command == "MESSAGE" or command == "SENDMESSAGE":
                            if count < 2:
                                output = "Invalid: input MESSAGE roomname yourmessage"
                                s.send(output)
                            else:
                                num = len(data.split())
                                re_message = ''
                                for i in range(2, num):
                                    re_message = re_message + data.split()[i]
                                is_room = False
                                print "Message to send: " + re_message
                                for c in self.room_list:
                                    if c.name == data.split()[1]:
                                        c.send_message(re_message)
                                        is_room = True
                                    if is_room == False:
                                        output = "No matching room found"
                                        s.send(output)

                    else:
                        s.close()
                        del self.sockets[s]

        server.close()

def create(name, client, socket, cList):
    if c_exists(name, cList) == True:
        output = "Room already exists. Joining channel %s..." % (name)
        socket.send(output)
        join(name, client, socket, cList)
    else:
        cList[name] = [[client, socket]]
        output = "Created room name %s" % (name)
        socket.send(output)
        return cList


class Channel:
    def __init__(self, name):
        self.name = name
        self.clients = {}

    def add_client(self, client_name, socket):
        self.clients[socket] = client_name
        # self.clients.append(client_name)

    def check_client(self, client_name):
        for key, value in self.clients.iteritems():
            if value == client_name:
                del self.clients[key]

    def remove_client(self, client_name):
        for key, value in self.clients.iteritems():
            if value == client_name:
                # self.clients.remove(client_name)
                del self.clients[key]
            else:
                print "Client not in channel"
    def remove_all(self):
        self.clients.clear()
    def memeber_list(self):
        mList = []
        for key, values in self.clients.iteritems():
            mList.append((self.clients[socket]))
        return mList
    def send_message(self, message):
        for key, value in self.clients.iteritems():
            msg = "Message from room " + self.name + ': ' + message
            key.send(message)

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

    def choices(message, sclient, cList):
        command = message.split()[0]
        count = len(re.findall(r'\w+',message))
        if command == "CREATE":
            if count != 2:
                output = "Invalid: input CREATE roomname"
                # send to client
                sclient.send(output)
            else:
                sender = "temp"
                # create channel
        elif command == "LEAVE":
            if count != 2:
                output = "Invalid: input LEAVE roomname"
                sclient.send(output)
            else:
                cLeave = get_user_name(socket, cList)
                leave(message.split()[1], cLeave, sclient,cList)
        elif command == "DISCONNECT":
            if count != 2:
                output = "Invalid: input DISCONNECT roomname"
                sclient.send(output)
            else:
                sender = "temp"

        elif command == "JOIN":
            if count == 2:
                sender = "temp"
                join(message.split()[1], sender, sclient,cList)
                # join channel
            else:
                output = "Invalid: please input at least one room/channel to join"
                sclient.send(output)
        elif command == "LISTROOM":
            if count != 1:
                output = "Invalid: only input LISTROOM"
                sclient.send(output)
            else:
                room_list = []
                # list rooms
                room_list(sclient,message.split()[1],cList)
        elif command == "LISTMEMBERS":
            if count != 1:
                output = "Invalid: input LISTMEMBERS roomname"
                sclient.send(output)
            else:
                mem_list = []
                member_list(sclient, message.split()[1], cList)
        elif command == "MESSAGE":
            c_mess(input, cList, sclient)

def c_mess(input, cList, sclient):
    message = "temp"

def get_user_name(client, cList):
    for [check1, check2] in cList['Global']:
        if check2 == client:
            return check1

def leave(cName, client, socket, cList):
    #  add in ability to remove channel once empty
    if inChannel(client, socket, cName, cList) == True:
        cList[cName].remove([client, socket])
        output = "You left the room"
        client.send(output)
        return cList
    else:
        output = "You are not in the room, so you cannot leave"
        client.send(output)
        return cList




def c_exists(name, cList):
    if name in cList.keys():
        return True
    else:
        return False


def join(name,client,socket,cList):
    if c_exists(name,cList) == True:
        if inChannel(client, socket, name, cList) == True:
            output = "Already in room"
            socket.send(output)
            return cList
        else:
            cList[name].append([client, socket])
            output = "Successfully joined room/channel"
            socket.send(output)
            return cList

    else:
        output = "Room/channel does not exist"
        socket.send(output)
        return cList


def inChannel(client, socket, name, cList):
    if c_exists(name, cList) == True:
        if [name, socket] in cList[name]:
            return True
        else:
            return False

    else:
        output = "Checking for room that user is already in not found"
        socket.send(output)


def room_list(socket, cList):
    print_list = []
    for key,value in cList.items():
        if key != 'Global':
            print_list.append(key)
    if print_list:
        socket.send(print_list)
    elif not print_list:
        output = "No rooms"
        socket.send(output)


def member_list(socket, cName,  cList):
    print_list = []
    if c_exists(cName, cList) == True:
        for [check1, check2] in cList[cName]:
            print_list.append(check1)
        if print_list:
            socket.send(print_list)
        elif not print_list:
            output = "No members in room"
            socket.send(output)

    else:
        output = "Room to check members in does not exist"
        socket.send(output)



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
