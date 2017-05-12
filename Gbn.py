#!/usr/bin/python3.6
# -*- coding:utf-8 -*-
import select
from random import random

# 设置主机号和端口
HOST = '127.0.0.1'
PORT = 8080

# 单次读取的最大字节数
BUFFER_SIZE = 2048

# 窗口与包序号长度
WINDOWS_LENGTH = 10
SEQ_LENGTH = 12

# 最大延迟时间
MAX_TIME = 3


class Segment():

    def __init__(self, msg, seq=0, state=0):
        self.msg = msg
        self.state = state
        self.seq = str(seq % SEQ_LENGTH)

    def __str__(self):
        return self.seq + ' ' + self.msg


class Gbn():

    def __init__(self, s):
        self.s = s

    def send_data(self, path, port):

        # 计时和包序号初始化
        time = 0
        seq = 0

        data_windows = []

        with open(path, 'r') as f:

            while True:

                # 当超时后，将窗口内的数据更改为未发送状态
                if time > MAX_TIME:
                    print('timeout!')
                    for data in data_windows:
                        data.state = 0

                # 窗口中数据少于最大容量时，尝试添加新数据
                while len(data_windows) < WINDOWS_LENGTH:
                    line = f.readline().strip()

                    if not line:
                        break

                    data = Segment(line, seq=seq)
                    data_windows.append(data)
                    seq += 1

                # 窗口内无数据则退出总循环
                if not data_windows:
                    self.s.sendto('test over!', (HOST, port))
                    print('test over!')
                    break

                # 遍历窗口内数据，如果存在未成功发送的则发送
                for data in data_windows:
                    if not data.state:
                        self.s.sendto(str(data), (HOST, port))
                        print('send segment ' + data.seq + ', msg is ' + data.msg)
                        data.state = 1

                # 无阻塞socket连接监控
                readable, writeable, errors = select.select([self.s, ], [], [], 1)

                if len(readable) > 0:

                    # 收到数据则重新计时
                    time = 0

                    message, address = self.s.recvfrom(BUFFER_SIZE)
                    print('receive ACK ' + str(message.split()[0]))

                    for i in range(len(data_windows)):
                        if message == data_windows[i].seq:
                            data_windows = data_windows[i+1:]
                            break
                else:
                    # 未收到数据则计时器加一
                    time += 1


    def recv_data(self):

        # 记录上一个回执的ack的值
        last_ack = SEQ_LENGTH - 1

        while True:

            readable, writeable, errors = select.select([self.s, ], [], [], 1)

            if len(readable) > 0:
                message, address = self.s.recvfrom(BUFFER_SIZE)

                if message == 'test over!':
                    break

                ack = int(message.split()[0])

                print('receive segment ' + str(ack) + ', msg is ' + str(message.split()[1]))

                # 连续接收数据则反馈当前ack
                if last_ack == (ack - 1) % SEQ_LENGTH:

                    # 丢包率为0.2
                    if random() < 0.2:
                        print('ACK loss!')
                        continue

                    self.s.sendto(str(ack), address)

                    print('send ACK ' + str(ack))

                    last_ack = ack

                else:
                    self.s.sendto(str(last_ack), address)
                    print('send ACK ' + str(last_ack))



class Sr(object):

    def __init__(self, s):
        self.s = s

    def send_data(self, path, port):

        # 计时和包序号初始化
        time = 0
        seq = 0

        data_windows = []

        with open(path, 'r') as f:

            while True:

                # 当超时后，将窗口内第一个发送成功未确认的数据状态更改为未发送
                if time > MAX_TIME:
                    print('timeout!')
                    for data in data_windows:
                        if data.state == 1:
                            data.state = 0
                            break

                # 窗口中数据少于最大容量时，尝试添加新数据
                while len(data_windows) < WINDOWS_LENGTH:
                    line = f.readline().strip()

                    if not line:
                        break

                    data = Segment(line, seq=seq)
                    data_windows.append(data)
                    seq += 1

                # 窗口内无数据则退出总循环
                if not data_windows:
                    print('test over!')
                    self.s.sendto('test over!', (HOST, port))
                    break

                # 遍历窗口内数据，如果存在未成功发送的则发送
                for data in data_windows:
                    if not data.state:
                        self.s.sendto(str(data), (HOST, port))
                        print('send segment ' + data.seq + ', msg is ' + data.msg)
                        data.state = 1

                readable, writeable, errors = select.select([self.s, ], [], [], 1)

                if len(readable) > 0:

                    # 收到数据则重新计时
                    time = 0

                    message, address = self.s.recvfrom(BUFFER_SIZE)
                    print('recieve ACK ' + str(message))

                    # 收到数据后更改该数据包状态为已接收
                    for data in data_windows:
                        if message == data.seq:
                            data.state = 2
                            break
                else:
                    # 未收到数据则计时器加一
                    time += 1

                # 当窗口中首个数据已接收时，窗口前移
                while data_windows[0].state == 2:
                    data_windows.pop(0)

                    if not data_windows:
                        break


    def recv_data(self):

        # 窗口的初始序号
        seq = 0
        data_windows = {}

        while True:

            readable, writeable, errors = select.select([self.s, ], [], [], 1)

            if len(readable) > 0:

                message, address = self.s.recvfrom(BUFFER_SIZE)

                if message == 'test over!':
                    break

                ack = message.split()[0]
                print('recieve segment ' + str(ack) + ', msg is ' + str(message.split()[1]))


                # 丢包率为0.2
                if random() < 0.2:
                    print('ACK loss!')
                    continue

                # 返回成功接收的包序号
                self.s.sendto(ack, address)
                print('send ACK ' + str(ack))
                data_windows[ack] = message.split()[1]

                # 滑动窗口
                while str(seq) in data_windows:
                    data_windows.pop(str(seq))
                    seq = (seq + 1) % SEQ_LENGTH

