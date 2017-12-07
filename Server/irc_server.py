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
        for s in self.sockets:
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
                        # print data
                        command = data.split()[0]
                        print "Command: " + command
                        # print data.split()
                        count = len(data.split())
                        # print count
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
                                    if c.name == data.split()[1]:
                                        c.remove_client(self.sockets[s])
                                        break

                        elif command == "DISCONNECT":
                            if count != 1:
                                output = "Invalid: input DISCONNECT"
                                s.send(output)
                            else:
                                for c in self.room_list:
                                    c.check_client(self.sockets[s])
                                # del self.sockets[s]
                                for key, value in self.sockets.items():
                                        if key == s:
                                            del self.sockets[s]
                                            print "Removed " + value + " from server."
                                # self.sockets.pop(s)
                                s.close()

                        elif command == "JOIN":
                            if count == 2:
                                found_room = False
                                for c in self.room_list:
                                    if c.name == data.split()[1]:
                                        output = "Joining channel..."
                                        s.send(output)
                                        c.add_client(self.sockets[s], s)
                                        found_room = True
                                        output = "Joined channel " + data.split()[1] + "\n"
                                        s.send(output)
                                if found_room == False:
                                    output = "No channel to join matching " + data.split()[1] + "\n"
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
                                    msg = "Room: " + output + "\n"
                                    s.send(msg)

                        elif command == "LISTMEMBERS" or command == "LISTMEM":
                            if count != 2:
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
                                    re_message = re_message + " " + data.split()[i]
                                is_room = False
                                # print "Message to send: " + re_message
                                for c in self.room_list:
                                    if c.name == data.split()[1]:
                                        c.send_message(self.sockets[s], re_message)
                                        is_room = True
                                if is_room == False: # place outside for?
                                    output = "Room name " + data.split()[1] + " not found\n"
                                    s.send(output)

                    else:
                        s.close()
                        del self.sockets[s]

        server.close()


class Channel:
    def __init__(self, name):
        self.name = name
        self.clients = {}

    def add_client(self, client_name, socket):
        self.clients[socket] = client_name
        # self.clients.append(client_name)

    def check_client(self, client_name):
        for key, value in self.clients.items():
            if value == client_name:
                del self.clients[key]

    def remove_client(self, client_name):
        for key, value in self.clients.items():
            if value == client_name:
                # self.clients.remove(client_name)
                del self.clients[key]

            else:
                print "Client not in channel"

    def remove_all(self):  # Unneeded. Used for testing
        self.clients.clear()

    def member_list(self):
        mList = []
        num = 1
        for key, values in self.clients.iteritems():
            num_str = str(num)
            msg = "Member #"+ num_str + ": " + self.clients[key] + "\n"
            num = num + 1
            mList.append((msg))
        return mList

    def send_message(self, member, message):
        for key, value in self.clients.iteritems():
            msg = "Message from room " + self.name + ' member ' + member + ": " + message + "\n"
            key.send(msg)


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

