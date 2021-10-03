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

DEBUG = False

HTTP_VERSION = "HTTP/1.1"
CRLF = "\r\n"


def help():
    print("httpclient.py [GET/POST] [URL]\n")


def log(*msg, sep="\n"):
    if (DEBUG):
        print(*msg, sep=sep)


class URL(object):
    def __init__(self, scheme, netloc, path, params, query, fragment, host, port):
        self.scheme = scheme
        self.netloc = netloc
        self.path = path
        self.params = params
        self.query = query
        self.fragment = fragment
        self.host = host
        self.port = port


class HTTPRequest(object):
    def __init__(self, method="GET", route="/", headers={}, body=""):
        self.method = method
        self.route = route
        self.headers = headers
        self.body = body

        self.headers["User-Agent"] = "Knockoff curl/7.74.0"

    def __str__(self) -> str:
        request_line = f"{self.method} {self.route} {HTTP_VERSION}\r\n"
        headers = "" if len(self.headers) == 0 else "\r\n".join(
            [f"{key}: {value}" for key, value in self.headers.items()]
        ) + "\r\n"
        body = "\r\n" + self.body
        message = request_line + headers + body
        return message


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self) -> str:
        return f"HTTPResponse Object:\n---Status Code---\n{self.code}\n---Body---\n{self.body}"


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        status_line_end = data.find(CRLF)
        status_line = data[:status_line_end]
        (version, code, reason) = status_line.split(" ", 2)
        return int(code)

    def get_headers(self, data):
        status_line_end = data.find(CRLF)
        headers_end = data.find(CRLF*2)
        headers = data[status_line_end + len(CRLF):headers_end]
        return headers

    def get_body(self, data):
        headers_end = data.find(CRLF*2)
        body = data[headers_end + 2*len(CRLF):]
        return body

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

    def parse_url(self, url):
        # Python Software Foundation, "URL Parsing"
        # 2021-09-05, https://docs.python.org/3.6/library/urllib.parse.html#url-parsing
        # PSF License Agreement and the Zero-Clause BSD license
        url_components = urllib.parse.urlparse(url)
        (scheme, netloc, path, params, query, fragment) = url_components
        host, port = url_components.hostname, url_components.port

        # Python Software Foundation, "URL Quoting"
        # 2021-09-05, https://docs.python.org/3/library/urllib.parse.html#url-quoting
        # PSF License Agreement and the Zero-Clause BSD license
        path = "/" if path == "" else urllib.parse.quote(path)
        
        host = socket.gethostbyname(host)
        port = 80 if port is None else port

        return URL(scheme, netloc, path, params, query, fragment, host, port)

    def encode_args(self, args: dict):
        # Python Software Foundation, "URL Quoting"
        # 2021-09-05, https://docs.python.org/3/library/urllib.parse.html#url-quoting
        # PSF License Agreement and the Zero-Clause BSD license
        terms = [f"{urllib.parse.quote_plus(key)}={urllib.parse.quote_plus(value)}" for key, value in args.items()]
        return "&".join(terms)

    def GET(self, url, args=None):
        url = self.parse_url(url)
        self.connect(url.host, url.port)

        route = url.path
        if args is not None:
            url.query = self.encode_args(args)
        if url.query != "":
            route = f"{url.path}?{url.query}"
        

        request = HTTPRequest("GET", route, {"Host": url.netloc})
        self.sendall(str(request))
        self.socket.shutdown(socket.SHUT_WR)
        log("Sending request...", request)

        data = self.recvall(self.socket)
        self.close()
        log("Receiving response...", data)

        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url = self.parse_url(url)
        self.connect(url.host, url.port)

        if args is None:
            body = ""
            headers = {
                "Host": url.netloc,
                "Content-Type": "text/plain",
                "Content-Length": 0
            }
        else:
            body = self.encode_args(args)
            headers = {
                "Host": url.netloc,
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": len(body.encode('utf-8'))
            }

        request = HTTPRequest("POST", url.path, headers, body)
        self.sendall(str(request))
        self.socket.shutdown(socket.SHUT_WR)
        log("Sending request...", request)

        data = self.recvall(self.socket)
        self.close()
        log("Receiving response...", data)

        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
