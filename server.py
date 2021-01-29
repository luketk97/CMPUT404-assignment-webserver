#  coding: utf-8 
import os
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Taekun(Luke) Kim
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    #receives a request and sends back a response 
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        req = self.data.decode().split("\r\n")[0].split()
        if req:
            req_type = req[0]
            req_addr = req[1]
        else: 
            req_type = ""
        if req_type == "GET":
            #return index.html file if request is a directory
            if req_addr.endswith("/"):
                path = os.getcwd() + "/www" + req_addr + "index.html"
            #if request is /deep, redirect to /deep/
            elif req_addr == "/deep":
                self.request.sendall(b"HTTP/1.1 301 Moved Permanently\n")
                self.request.sendall(b"Location: http://127.0.0.1:8080/deep/\n")
                self.request.sendall(b"Content-Type: text/html \n")
                self.request.sendall(b"Connection: close \n\n")
                self.request.sendall(b"<html><body>Page Moved Permanently http://127.0.0.1:8080/deep/</body></html>\n")
            #else, return request in /www directory
            else:
                path = os.getcwd() + "/www" + req_addr
            try:
                #blocks access of directories above /www
                if req_addr.startswith("/.."):
                    raise Exception
                #checks the filetype of the given request
                filetype = path.split(".")[1]
                with open(path , 'rb') as f:
                    #sends a 200 http response header with content type header and body
                    self.request.sendall(b"HTTP/1.1 200 OK\n")
                    self.request.sendall(bytearray(f'Content-Type: text/{filetype}\n', 'utf-8'))
                    self.request.sendall(b"Connection: close \n\n")
                    for line in f.readlines():
                        self.request.sendall((line))
                    self.request.sendall(b'\n')
            #if requested file does not exist, return 404 response
            except IOError:
                self.request.sendall(b"HTTP/1.1 404 Not Found\n")
                self.request.sendall(b"Content-Type: text/html \n")
                self.request.sendall(b"Connection: close \n\n")
                self.request.sendall(b"<html><body>404 Page Not Found</body></html>\n")
            #if the request does not specify file type, return 404 response
            except IndexError:
                self.request.sendall(b"HTTP/1.1 404 Not Found\n")
                self.request.sendall(b"Content-Type: text/html \n")
                self.request.sendall(b"Connection: close \n\n")
                self.request.sendall(b"<html><body>404 Wrong Name</body></html>\n")
            #if the request is a directory above /www, return 404 response
            except Exception:
                self.request.sendall(b"HTTP/1.1 404 Not Found\n")
                self.request.sendall(b"Content-Type: text/html \n")
                self.request.sendall(b"Connection: close \n\n")
                self.request.sendall(b"<html><body>404 Directory Not Allowed</body></html>\n")
            
        #return 405 response for any request that is not GET
        else:
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\n")
            self.request.sendall(b"Content-Type: text/html \n")
            self.request.sendall(b"Connection: close \n\n")
            self.request.sendall(b"<html><body>Method Not Allowed</body></html>\n")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
