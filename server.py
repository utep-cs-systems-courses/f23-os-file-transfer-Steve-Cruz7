#! /usr/bin/env python3

import socket, sys, re, os
sys.path.append("lib")
import params, buffers, frame

switchesVarDefaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),     #Setting up map for params
    (('-?', '--usage'), "usage", False),
    )

progname = "labserver"
paramMap = params.parseParams(switchesVarDefaults)


listenPort = paramMap['listenPort']
listenAddr = ''                                        #Taking all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #IPV4 and Stream Sockets?
s.bind((listenAddr, listenPort))                       #binding socket to listenPort
s.listen(1)                                            #turning s into a listener and allowing up to 1 msg in queue

conn, addr = s.accept()                                #accepting incoming connection and get socket descriptor of that connection
print('Connected by', addr)

writer = buffers.BufferedFdWrite(conn.fileno())
while 1:
    flag = frame.frame("x", conn.fileno())
    if flag == 0:
        print("Zero length read, nothing to send, terminating...")
        break
    received = "Message Received!".encode()
    for byte in received:
        writer.writeByte(byte)
    writer.flush()

conn.shutdown(socket.SHUT_WR)
#conn.close()
