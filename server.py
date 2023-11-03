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

pidAddr = {}                                           #for active connections: maps pid->client addr

if paramMap['usage']:
    params.usage()

def chatWithClient(connAddr):
    sock, addr = connAddr
    print(f'Child : pid= {os.getpid()} connected to client at {addr}')
    frame.frame("x", sock.fileno())
    print("--FILE TRANSFER COMPLETE--TURNING INTO ZOMBIE");
    sock.shutdown(socket.SHUT_WR)
    sys.exit(0)

    

    

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #IPV4 and Stream Sockets

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.settimeout(5)

s.bind((listenAddr, listenPort))                       #binding socket to listenPort

s.listen(1)                                            #turning s into a listener and allowing up to 1 msg in queue


while True:
    # reap zombie children (if any)
    while pidAddr.keys():
        # Check for exited children (zombies).  If none, don't block (hang)
        if (waitResult := os.waitid(os.P_ALL, 0, os.WNOHANG | os.WEXITED)): 
            zPid, zStatus = waitResult.si_pid, waitResult.si_status
            print(f"""zombie reaped:
            \tpid={zPid}, status={zStatus}
            \twas connected to {pidAddr[zPid]}""")
            del pidAddr[zPid]
        else:
            break               # no zombies; break from loop
    print(f"Currently {len(pidAddr.keys())} clients")

    try:
        connSockAddr = s.accept() # accept connection from a new client
    except TimeoutError:
        connSockAddr = None 

    if connSockAddr is None:
        continue
        
    forkResult = os.fork()     # fork child for this client 
    if (forkResult == 0):      # child
        s.close()              # child doesn't need listenSock
        chatWithClient(connSockAddr)
    # parent
    sock, addr = connSockAddr
    sock.close()   # parent closes its connection to client
    pidAddr[forkResult] = addr
    print(f"spawned off child with pid = {forkResult} at addr {addr}")

