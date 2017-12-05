from SimpleHTTPServer import SimpleHTTPRequestHandler
import sys
import socket
import os
import signal
import shutil
import select
import re


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


class ServerMain:
    def __init__(self, port):
        self.sockets = 0
        self.cList = []
        # Socket List
        self.sockets = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', port))
        self.server.listen(5)  # Max backlog value
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        print "Exiting"
        for s in socket:
            s.close()
            self.server.close()
            sys.exit(0)

    def connect(self):
        self.sockets = []
        input = [self.server, sys.stdin]
        running = 1
        cList = {'Global': []}  # Dictionary
        while running:
            print "Running"
            try:
                inputready, outputready, exceptready = select.select(input, [], [])
            except select.error, e:
                print "select error\n"
                break
            for s in inputready:
                print "In for loop"
                if s == self.server:
                    print "Waiting for client"
                    client, address = server.accept()
                    print "Accepted client"
                    client_name = client.split('Name: ')[1]  # take name from client and set it as their name     #receive(client).split('NAME: ')[1]   # NOT DONE
                    cList['Global'].append([client_name, client])
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
                        # s.send(data)
                        Room.choices(data, s, cList)
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

    def choices(message, sclient, cList):
        command = message.split()[0]
        count = len(re.findall(r'\w+',message))
        if command == "CREATE":
            if count !=2:
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


def create(name, client, socket, cList):
    if c_exists(name, cList) == True:
        output = "Room already exists. Joining channel %s..." % (name)
        socket.send(output)
        join(name,client,socket,cList)
    else:
        cList[name] = [[client, socket]]
        output = "Created room name %s" % (name)
        socket.send(output)
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
