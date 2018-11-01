#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import rri

def rri_check_request():
    request = []
    request.append("Action: CHECK")
    request.append("Version: 2.0")
    request.append("Domain: denic.de")
    return request

rricli = rri.RriClient("rri.test.denic.de",51131)
rricli.login("MyLogin","MyPassword")
rricli.sendRequest(rri_check_request())
rricli.getResponse()
rricli.logout()
rricli.shutdown()

RRI Python Libary als rri.py speichern:

#/usr/bin/env python3

import socket
import ssl
from struct import pack, unpack
import time

class AuthorizationError(Exception):
    def __init__(self, message, additional):
        super(AuthorizationError, self).__init__(message)
        self.additional = additional

class RriClient:
    def __init__(self,rrihost,rriport):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sslSocket = ssl.wrap_socket(self.socket)
        self.sslSocket.connect((rrihost,rriport))

    def shutdown(self):
        self.sslSocket.close()

    def sendMsg(self,data):
        msg = "\n".join(data)
        msg += "\n"
        msglen = len(msg)
        header = struct.pack("!L",msglen)

        self.sslSocket.write(header)
        self.sslSocket.write(msg)

    def getResponse(self):
        resp_header = self.sslSocket.read(4)
        size = int(unpack('!i', resp_header)[0])
        data = ""
        rest = size
        while len(data) < size:
            packet = self.sslSocket.read(rest)
            data += packet
            rest -= len(packet)
        return data

    def sendRequest(self,data):
        self.sendMsg(data)

    def login(self,username,password):
        data = []
        data.append("Action: LOGIN")
        data.append("Version: 2.0")
        data.append("User: " + username)
        data.append("Password: " + password)
        self.sendRequest(data)
        answer = self.getResponse()
        if "RESULT: success" not in answer:
            raise AuthorizationError("could not login [username=" + str(username) + "]",
                                     answer)
            
    def logout(self):
        data = []
        data.append("Action: LOGOUT")
        data.append("Version: 2.0")

        self.sendMsg(data)
        self.getResponse()

