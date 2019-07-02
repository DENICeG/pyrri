#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import socket
import ssl
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from struct import pack, unpack


class AuthorizationError(Exception):

    def __init__(self, message, additional):
        super(AuthorizationError, self).__init__(message)
        self.additional = additional


class RRIError(Exception):

    def __init__(self, message, additional):
        super(RRIError, self).__init__(message)
        self.additional = additional


class RRIClient(object):

    def __init__(self):
        self.ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        # self.ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.load_default_certs()
        self.socket = None

    def load_ssl_trustanchor(self, filename):
        self.ssl_ctx.load_verify_locations(cafile=filename)
        self.ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    def connect(self, host, port):
        if self.socket:
            self.disconnect()
        self.socket = self.ssl_ctx.wrap_socket(socket.socket(socket.AF_INET))
        self.socket.connect((host, port))

    def check_ssl_cert(self, certname):
        cert = self.socket.getpeercert(binary_form=False)
        ssl.match_hostname(cert, certname)

    def login(self, username, password):
        payload = "version: 3.0\n" + \
                "action: LOGIN\n" + \
                "user: " + str(username) + "\n" + \
                "password: " + str(password) + "\n"
        answer = self.talk(payload)
        if "RESULT: success" not in answer:
            raise AuthorizationError("could not login [username=" + str(username) + "]",
                                     answer)

    def _send_data(self, data):
        payload = bytes(data, "utf-8")
        size = pack('!i', len(payload))
        self.socket.send(size)
        self.socket.send(payload)

    def _read(self, bytes):
        data = b""
        rest = bytes
        while len(data) < bytes:
            packet = self.socket.recv(bytes)
            data += packet
            rest -= len(packet)
        return data

    def _read_data(self):
        data = self._read(4)
        size = int(unpack('!i', data)[0])
        return self._read(size).decode("utf-8")

    def talk(self, data):
        self._send_data(data)
        return self._read_data()

    def logout(self):
        payload = "version: 3.0\n" + \
                "action: LOGOUT\n"
        answer = self.talk(payload)
        if "RESULT: success" not in answer:
            raise RRIError("could not logout", answer)

    def disconnect(self):
        self.socket.close()
        del self.socket
        self.socket = None

#########################################################################################################
# commandline client
#########################################################################################################


def get_args():
    parser = ArgumentParser(description='RRI-Client',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--server', type=str, dest='server', default='rri.denic.de:51131',
                        help='Hostname and port of rri-server. or IP-address of RRI-server')
    parser.add_argument('-u', '--user', type=str, dest='username',
                        help='Username for RRI-server. For more security, this can '
                        'also be set by environment variable RRI_USERNAME')
    parser.add_argument('-p', '--password', type=str, dest='password',
                        help='Password for RRI-server. For more security, this can '
                        'also be set by environment variable RRI_PASSWORD')
    parser.add_argument('-i', '--input', type=str, dest='input',
                        help='Filename with order to send to RRI. When skipping this '
                        'parameter, the order is read from stdin')
    parser.add_argument('-o', '--output', type=str, dest='output',
                        help='Filename in which the answer from RRI is stored. '
                        'When skipping this parameter, answer is written to stdout')

    return parser.parse_args()


def get_order(filename):
    if not filename:
        return "".join(sys.stdin)
    with open (filename, "r") as handle:
            return handle.read()


def write_answer(filename, answer):
    if not filename:
        print (answer)
    else:
        with open (filename, "w") as handle:
            return handle.write(answer)


def get_credentials(args):
    username = os.getenv("RRI_USERNAME", None)
    password = os.getenv("RRI_PASSWORD", None)
    if args.username:
        username = args.username
    if args.password:
        password = args.password
    return (username, password)


def get_server(args):
    if ":" in args.server:
        (hostname, port) = args.server.split(':')
    else:
        hostname = args.server
        port = 51131
    return (hostname, port)

#########################################################################################################
# Main
#########################################################################################################


if __name__ == "__main__":
    args = get_args()

    (hostname, port) = get_server(args)
    if not port or int(port) == 0:
        port = '51131'
    (username, password) = get_credentials(args)
    if not username or not password:
        print ("ERROR: username and/or password is missing")
        sys.exit(1)

    try:
        order = get_order(args.input)
        rri = RRIClient()
        rri.connect(hostname, int(port))
        # rri.check_ssl_cert(config.rri_certname)
        rri.login(username, password)
        answer = rri.talk(order)
        rri.logout()
        rri.disconnect()

        write_answer(args.output, answer)
    except BaseException as exp:
        print ("ERROR: " + str(exp))
        sys.exit(1)

