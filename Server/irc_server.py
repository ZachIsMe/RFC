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
sys.setdefaultencoding('UTF8')
input = [server, sys.stdin]
running = 1
while running:
    try:
        inputready,outputready,exceptready = select.select(input,[],[])
    except select.error, e:
        print "select error\n"
        break



    for s in inputready:
        if s == server:
            client, address = server.accept()
            clientName = recieve(conn)
            input.appent(client)
        elif s == sys.stdin:
            junk = sys.stdin.readline()
            running = 0
        else:
            data = s.recv(size)
            if data:
                s.send(data)
            else:
                s.close()
                input.remove(s)
server.close()

def create_room(cname, client):




class Room:
    def __init__(self):  # Default constructor
        self.name = "General"  # Change later to pass in name from client in class declaration
        self.sockets = []


    def client_joined(self, a_client):
        welcome_message = "Hello, " + a_client.name + "! Welcome to Room " + self.name + "!"



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