#! /usr/bin/env python3

#client side
import socket, sys, re, os
sys.path.append("lib")
import params
import frame, buffers

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "labClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    try:
        print("attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

#Adding delays here if necessary


if s is None:
    print('could not open socket')
    sys.exit(1)

frame.frame("c", s.fileno())                         #sending file information after framing

s.shutdown(socket.SHUT_WR)

#Maybe add something here to receive any confirmation transmissions
while 1:
    data = s.recv(1024).decode()
    print("Received '%s'" % data)
    if len(data) == 0:
        break;
print("Zero length read. Closing")

#Proposition for handling stammering proxy: Use buffered reader to hold data in buffer until certain threshold is reached
#For example, when waiting for the first 8 bytes since Im an OutOfBander, I can wait until the buffer has a length of 8 and then read a filename
#And then repeat this for the second part of the deframer.


s.close()
