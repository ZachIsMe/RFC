import irc_server


class IRCServer:
    def __init__(self, port):
        self.port = port


    def keyboardInterrupt(self):
        print "Shutting down"


if __name__ == "__main__":
    run_server = irc_server.ServerMain(6667)
    run_server.connect()