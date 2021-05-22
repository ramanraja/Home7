#! /usr/bin/python3
# Q&D Python NTP server
# Use it with any of the NTP clients
# https://wiki.python.org/moin/UdpCommunication

import socket, struct, sys, time, datetime

server_ip = "0.0.0.0"
server_port = 123
FIRST_BYTE = 0x1C
FORMAT = '!' + 'B'*4 + 'I'*11
OFFSET_1970 =  2208988800        #  No. of seconds in 70 years (1970-1900)

def make_payload ():
    ts = time.time()
    print (time.ctime(ts))
    #print (ts)            # 1621531143.9885082
    #print (type(ts))      # <class 'float'>
    ots = int(ts) + OFFSET_1970  
    payload = struct.pack (
        FORMAT,
        FIRST_BYTE,0,0,0,
        0,0,0, 0,0,0, 0,0,0,
        ots,
        0
    )
    #print (payload)
    #print (type(payload))
    return payload
       
def print_rx_request (data):
    for b in data:
        print (hex(b), end=' ')  
    print ('<end>\n') 
#---------------------------------------------------------------
# main
#---------------------------------------------------------------
        
print ('\nQ&D NTP server starting...')
#print (FIRST_BYTE)
#print (FORMAT)
skt = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
skt.bind ((server_ip, server_port))
print  ("Serving UDP from: ", skt.getsockname())
 
while True:
    try:                 
        data, addr = skt.recvfrom (128)
        print ("Received {} bytes from {}".format (len(data), addr)) 
        #print_rx_request (data)
        payload = make_payload ()           
        skt.sendto (payload, (addr))  # NOTE: addr is a 2-tuple
    except KeyboardInterrupt:
        skt.close()
        print ("Bye!")
        break
    except Exception as e:
        print (str(e))