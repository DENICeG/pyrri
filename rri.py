#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""!DENIC RRI module and commandline client
"""

import os
import sys
import socket
import ssl
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from struct import pack, unpack

__author__ = "Patrick Fedick"
__copyright__ = "Copyright 2019, DENIC eG"
__license__ = "MIT"
__email__ = "fedick@denic.de"
__status__ = "Prototype"


class AuthorizationError(Exception):

    def __init__(self, message, additional):
        super(AuthorizationError, self).__init__(message)
        self.additional = additional


class RRIError(Exception):

    def __init__(self, message, additional):
        super(RRIError, self).__init__(message)
        self.additional = additional


class RRIClient(object):
    """!RRI Client Module
    """

    def __init__(self):
        self.ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        # self.ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.load_default_certs()
        self.socket = None

    def load_ssl_trustanchor(self, filename):
        """!Load SSL trustanchor

        When calling this method the contents of filename get loaded as trustanchor
        and on connection the certificate of the RRI server is checked against it.
        @param filename File with Certificates in PEM format
        """
        self.ssl_ctx.load_verify_locations(cafile=filename)
        self.ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    def connect(self, host, port=51131):
        """!Connect to RRI server

        @param host hostname or IP address of RRI server
        @param port optional TCP port of RRI server, default=51131
        """
        if self.socket:
            self.disconnect()
        self.socket = self.ssl_ctx.wrap_socket(socket.socket(socket.AF_INET))
        self.socket.connect((host, port))

    def check_ssl_cert(self, certname):
        """!Checks the certname against the certificate presented by RRI server

        Call this method after connection to RRI server is established, to check if the
        certificate presented by the server contains the expected name.
        @param certname Name of certificate
        @raise CertificateError is raised when certname does not match
        """
        cert = self.socket.getpeercert(binary_form=False)
        ssl.match_hostname(cert, certname)

    def login(self, username, password):
        """!Login to RRI server

        @param username string with username/login
        @param password string with password
        @raise AuthorizationError is raised when credentials are unknown to RRI server
        """
        payload = "version: 4.0\n" + \
                "action: LOGIN\n" + \
                "user: " + str(username) + "\n" + \
                "password: " + str(password) + "\n"
        answer = self.talk(payload)
        if "RESULT: success" not in answer:
            raise AuthorizationError("could not login [username=" + str(username) + "]",
                                     answer)

    def _send_data(self, data):
        """!Internal method: sends data to RRI server

        @param data string with order send to RRI server
        """
        payload = bytes(data, "utf-8")
        size = pack('!i', len(payload))
        self.socket.send(size)
        self.socket.send(payload)

    def _read(self, size):
        """!Internal method: reads bytes from RRI server

        @param bytes integer with amount of bytes to read from RRI server
        @return binary data from socket
        """
        data = b""
        rest = size
        while len(data) < size:
            packet = self.socket.recv(rest)
            data += packet
            rest -= len(packet)
        return data

    def _read_data(self):
        """!Internal method: reads answer from RRI server

        @return string with answer
        """
        data = self._read(4)
        size = int(unpack('!i', data)[0])
        return self._read(size).decode("utf-8")

    def talk(self, data):
        """!Send order to RRI server and read the answer

        @param data string which is send to RRI server. Can be key-/value- or xml-format.
        @return string with answer
        @note answer is not checked if RRI indicated an error
        """
        self._send_data(data)
        return self._read_data()

    def logout(self):
        """!Logout from RRI server

        @raise RRIError is raised when logout failed
        """
        payload = "version: 4.0\n" + \
                "action: LOGOUT\n"
        answer = self.talk(payload)
        if "RESULT: success" not in answer:
            raise RRIError("could not logout", answer)

    def disconnect(self):
        """!Disconnect from RRI server
        """
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
    with open(filename, "r") as handle:
        return handle.read()


def write_answer(filename, answer):
    if not filename:
        print(answer)
    else:
        with open(filename, "w") as handle:
            handle.write(answer)


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


def main():
    args = get_args()
    (hostname, port) = get_server(args)
    if not port or int(port) == 0:
        port = '51131'
    (username, password) = get_credentials(args)
    if not username or not password:
        print("ERROR: username and/or password is missing")
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
        print("ERROR: " + str(exp))
        sys.exit(1)


if __name__ == "__main__":
    main()
