#!/usr/bin/python2.7
# -*- coding:utf-8 -*-
import socket
from Gbn import *

addr = (HOST, PORT)

if __name__ == '__main__':
    #建立客户端UDP套接字
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    while True:

        command = raw_input('please input you command : ')
        s.sendto(command, addr)
        
        if command == 'time':
            recvdata, addr = s.recvfrom(BUFFER_SIZE)
            print('server time is ' + recvdata)
        elif command == 'quit':
            recvdata, addr = s.recvfrom(BUFFER_SIZE)
            print('recieve reply : ' + recvdata)
            print('close socket!')
            s.close()
            break
        elif command == 'testgbn':
            p = Sr(s)
            p.recv_data()
            print('test over!')


