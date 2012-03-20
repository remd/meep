from meep_example_app import MeepExampleApp, initialize
import urllib
import os.path
import sys
import datetime
import socket
import threading

global _status
global _headers
# the function we will use to pass to __call__
def fake_start_response(status, headers):
    global _status
    global _headers
    _status = status
    _headers = headers

# handle a connection
def handle_connection(sock):
    while 1:
        try:
            data = ''
            while 1:
                x = sock.recv(1)
                data += x
                if data[-4:] == "\r\n\r\n":
                    break
            if not data:
                break

            #print "data:", (data,)

            # we need to check for POST and grab the Content-Length integer
            tmp = data
            tmp.strip()
            allLines = tmp.split("\r\n")
            # get request type
            request = allLines.pop(0)
            requestInfoList = request.split(' ')
            if requestInfoList[0] == "POST":
                contentLength = 0
                # get the content length
                for line in allLines:
                    splitLine = line.split(':', 2)
                    if splitLine[0].lower() == 'content-length':
                        contentLength = splitLine[1].strip()
                # now we loop a sock.recv of size 1 to get all POST data
                # the Content-Length header denotes how long the POST data is
                # eg. 45 = 45 bytes, so sock.recv(1) 45 times
                contentLength = int(contentLength)
                if contentLength > 0:
                    i = 0
                    while i < contentLength:
                        x = sock.recv(1)
                        data += x
                        i += 1
                #print "data:", (data,)

            sock.sendall(handle_request(data))
            sock.close()
            break

        except socket.error:
            break

# interpret the HTTP request and respond
def handle_request(request):
    request.strip()
    allLines = request.split("\r\n")

    # read request line
    request = allLines.pop(0)
    # split on whitespace
    requestInfoList = request.split(' ')
    #print requestInfoList

    fullQueryList = requestInfoList[1].split('?')
    #print fullQueryList

    form_dict = {}

    # no variables in URL to parse
    if len(fullQueryList) == 1:
        path_info = fullQueryList[0]
    # we need to do further processing on the variables (GET request)
    else:
        path_info = fullQueryList[0]
        tmpVariables = fullQueryList[1].split('&')
        for variablePair in tmpVariables:
            key,value = variablePair.split('=')
            form_dict[key] = urllib.unquote_plus(value)

    # scoop up the odd case (POST request)
    if requestInfoList[0] == "POST":
        post_variables = allLines[-1]
        tmpVariables = post_variables.split('&')
        for variablePair in tmpVariables:
            if variablePair != '':
                key,value = variablePair.split('=')
                form_dict[key] = urllib.unquote_plus(value)

    cookie = ''
    # get the cookie
    for line in allLines:
        tmp = line.split(':', 2)
        if tmp[0].lower() == 'cookie':
            cookie = tmp[1].strip()

    #print 'cookie = ', cookie

    environ = {} # make a request dictionary
    environ['PATH_INFO'] = path_info
    environ['wsgi.input'] = ''
    environ['HTTP_COOKIE'] = cookie
    if len(form_dict):
        environ['QUERY_STRING'] = urllib.urlencode(form_dict)

    data = app(environ, fake_start_response)

    response = ""
    #response += "HTTP/1.1 200 OK\r\n"
    response += "HTTP/1.1 %s\r\n" % (_status)
    response += "Date: %s \r\n" % datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S EST")
    response += "Server: WSGIServer/0.1 Python/2.5\r\n"
    for k,v in _headers:
        if k == 'Content-type':
            response += "Content-type: %s\r\n" % v
    for k,v in _headers:
        if k == 'Location':
            response += "Location: %s\r\n" % v
    for k,v in _headers:
        if k == 'Set-Cookie':
            response += "Set-Cookie: %s\r\n" % v
    # this is a dumb but necessary if-else block
    if type(data) is str:
        response += "Content-Length: %d\r\n\r\n" % (len(data))
        response += data
    elif type(data) is list:
        response += "Content-Length: %d\r\n\r\n" % (len(data[0]))
        response += data[0]

    #print "===== HTTTP RESPONSE CONTENTS ====="
    #print response

    # return the response
    return response

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
        
        t = threading.Thread(target=handle_connection, args=(client_sock,))
        print "Starting thread"
        t.start()
