#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Modifications copyright 2021 Diego Becerra
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

HTTP_VERSION = "HTTP/1.1"


def help():
    print("httpclient.py [GET/POST] [URL]\n")

    def __str__(self) -> str:
        return f"Status Code:{self.code}\nBody:{self.body}"


class HTTPRequest(object):
    def __init__(self, method="GET", route="/", headers={}, body=""):
        self.method = method
        self.route = route
        self.headers = headers
        self.body = body

        self.headers["Host"] = "27.0.0.1:27606"
        #self.headers["User-Agent"] = "curl/7.74.0"
        #self.headers["Accept"] = "*/*"

    def __str__(self) -> str:
        request_line = f"{self.method} {self.route} {HTTP_VERSION}\r\n"
        headers = "" if len(self.headers) == 0 else "\r\n".join([f"{key}: {value}" for key, value in self.headers.items()]) + "\r\n"
        body = "\r\n" + self.body
        message = request_line + headers + body
        return message


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        #host = socket.gethostbyname("slashdot.org")
        #port = 80
        host = "127.0.0.1"
        port = 27606

        self.connect(host, port)
        request = str(HTTPRequest("GET", "/dsadsadsadsa"))
        print("---------------------")
        print(request)

        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)
        
        response = self.recvall(self.socket)
        self.close()
        print("---------------------")
        print(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
