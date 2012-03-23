from meep_example_app import MeepExampleApp, initialize
import connection_handler

import socket
import threading

if __name__ == "__main__":
    app = MeepExampleApp()
    interface = "localhost"
    port = 8000

    #print "binding", interface, port
    print "Homework 8 Threaded Socket Server"
    print "Serving HTTP on port 8000..."
    sock = socket.socket()
    sock.bind( (interface, port) )
    sock.listen(5)

    while 1:
        (client_sock, client_address) = sock.accept()
        print "Got connection", client_address
        
        t = threading.Thread(target=connection_handler.handle_connection, args=(client_sock,app,))
        print "Starting thread"
        t.start()
