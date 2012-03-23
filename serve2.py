from meep_example_app import MeepExampleApp, initialize
import connection_handler

import sys
import socket

if __name__ == "__main__":
    app = MeepExampleApp()
    interface = "localhost"
    port = 8000

    #print "binding", interface, port
    print "Homework 7 Socket Server"
    print "Serving HTTP on port 8000..."
    sock = socket.socket()
    sock.bind( (interface, port) )
    sock.listen(5)

    while 1:
        # this should allow the sock to never get 'stuck' open
        # doesn't work, still gets stuck occasionally
        # too tired to care // it works after the 60 second unix timeout
        try:
            #print "waiting..."
            (client_sock, client_address) = sock.accept()
            #print "connection established...", client_address
            # handle the connection
            connection_handler.handle_connection(client_sock, app)
        except KeyboardInterrupt:
            print
            try:
                sock.close()
                sys.exit()
            except:
                sys.exit()

