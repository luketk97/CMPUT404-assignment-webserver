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
            if req_addr.endswith("/"):
                path = os.getcwd() + "/www" + req_addr + "index.html"
            elif req_addr == "/deep":
                self.request.sendall(b"HTTP/1.1 301 Moved Permanently\n")
                self.request.sendall(b"Location: http://127.0.0.1:8080/deep/\n")
                self.request.sendall(b"Content-Type: text/html \n\n")
                self.request.sendall(b"<html><body>Page Moved Permanently http://127.0.0.1:8080/deep/</body></html>\n")
            else:
                path = os.getcwd() + "/www" + req_addr
            try:
                if "/../" in req_addr:
                    raise Exception
                filetype = path.split(".")[1]
                with open(path , 'rb') as f:
                    self.request.sendall(b"HTTP/1.1 200 OK\n")
                    self.request.sendall(bytearray(f'Content-Type: text/{filetype}\n\n', 'utf-8'))
                    for line in f.readlines():
                        self.request.sendall((line))
                    f.close()
        
            except IOError:
                self.request.sendall(b"HTTP/1.1 404 Not Found\n")
                self.request.sendall(b"Content-Type: text/html \n\n")
                self.request.sendall(b"<html><body>404 Page Not Found</body></html>\n")
            except IndexError:
                self.request.sendall(b"HTTP/1.1 404 Not Found\n")
                self.request.sendall(b"Content-Type: text/html \n\n")
                self.request.sendall(b"<html><body>404 Wrong Name</body></html>\n")
            except Exception:
                self.request.sendall(b"HTTP/1.1 404 Not Found\n")
                self.request.sendall(b"Content-Type: text/html \n\n")
                self.request.sendall(b"<html><body>404 Directory Not Allowed</body></html>\n")
            

        elif req and req_type != "GET":
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\n")
            self.request.sendall(b"Content-Type: text/html \n\n")
            self.request.sendall(b"<html><body>Method Not Allowed</body></html>\n")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
