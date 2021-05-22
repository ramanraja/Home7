#! /usr/bin/python3
# NTP client
# https://stackoverflow.com/questions/39466780/simple-sntp-python-script
# Protocol: https://labs.apnic.net/?p=462
# example: https://github.com/python-trio/trio/blob/master/notes-to-self/ntp-example.py

import socket, struct, sys, time, datetime

NTP_SERVER  =  '127.0.0.1'       # '0.uk.pool.ntp.org'
OFFSET_1970 =  2208988800        #  No. of seconds in 70 years (1970-1900)
FIRST_BYTE  =  0xDB  # version 3
 

def send_request (server, port):
    packet = bytearray(48)
    packet[0] = FIRST_BYTE

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as skt:
        skt.settimeout (4)
        try:
            skt.sendto (packet, (server, port))  # TODO: make this async
            data, address = skt.recvfrom (64)  # TODO: make this async
        except socket.timeout:
            print ('Timed out.')
            return
        except Exception as e:
            print ('EXCEPTION:' +str(e))
            return
            
        if data: 
            print ('\nResponse received from {} : {} bytes'.format (address, len(data)))
            ts = struct.unpack ('!12I', data)[10]   
            t = ts  - OFFSET_1970  # ts is the number of seconds since 1900
            print ('Time = %s' % time.ctime(t))
        
if __name__ == '__main__':

    server = NTP_SERVER
    port = 123
    if (len(sys.argv) > 1):
        server = sys.argv[1]
    print ("\nNTP client starting..")
    print ("Contacting server: ", server)
    try:
        while True:
            send_request (server, port)
            time.sleep (10)
    except KeyboardInterrupt:
        print ("Bye!")
    
'''-----------------------------------------------------

Time servers:
  0.uk.pool.ntp.org
Indian NTP servers:
  0.in.pool.ntp.org
  1.in.pool.ntp.org
  2.in.pool.ntp.org
  3.in.pool.ntp.org

struct.unpack ('!12I', data)[10]   
! stands for big endian format (the Network format)
12I is 12 blocks of 4-byte unsigned integers = 48 bytes
Our timestamp is in bytes 40-43, ie, 10th block (in zero based counting)
        
Request:
Send the first byte as 0xDB followed by 47 zeros.
1101 1011 = 11 011 011
11  = unknown leap second
011 = NTP version 3
011 = Client mode 

For NTP version 4, use the first byte: 0xE3
11 100 011 = 1110 0011

Response:
The first byte from any standard NTP server is 0x1C for version 3:
0001 1100 = 00 011 100
00  = no leap second
011 = NTP version 3
100 = Server mode 
 
-------------------------------------------------------'''    