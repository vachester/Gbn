#!/usr/bin/python2.7
# -*- coding:utf-8 -*-
import socket
import datetime
from Gbn import *


if __name__ == '__main__':
    # 建立服务器端UDP套接字
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))

    while True:

        data, addr = s.recvfrom(BUFFER_SIZE) 

        if data == 'time':
            now_time = datetime.datetime.now()
            time_str = datetime.datetime.strftime(now_time,'%Y-%m-%d %H:%M:%S')
            print('send time ' + str(time_str))
            s.sendto(str(time_str), addr)
        elif data == 'quit':
            reply = 'Good Bye!'
            print('send reply Good Bye!')
            s.sendto(reply, addr)
        elif data == 'testgbn':
            print('begin to test gbn protocol...')
            p = Sr(s)
            p.send_data('data.txt', addr[1])

    



