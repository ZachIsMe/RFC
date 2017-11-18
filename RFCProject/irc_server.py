from SimpleHTTPServer import SimpleHTTPRequestHandler
import sys, socket

# socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = ''  # could instead pass in '' in bind tuple
port = int(sys.argv[1])
sock.bind((host, port))  # passing tuple as single argument

# accept call from client
sock.listen(5)  # max one queued connection. Min 0

# initialization total
IT = ''

# initialize client socket
csock = []

# number of clients
numc = 2


# accept from client
for i in range(numc):
    (client, ap) = sock.accept()
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

sock.close()
print 'Initialization Total is ', IT