import socket
import threading
import time
from collections import deque
import math


class selective_repeat:
    @classmethod
    def __init__(self, addr, port):
        self.acked = {}
        self.addr = addr
        self.port = port
        self.seq = 0
        self.curr_download = {}
        self.nextpckt = 1
        self.expct_ack = list
        self.window_size = 4
        self.window = tuple(1, 1)
        self.timeout = 4
        # self.sum_of_packets = math.ceil(self.size_of_file / 2022)
        self.udp_server_socket = None
        self._init_socket()
        self.ack_th = threading.Thread(target=self.recieve_Acks, args=())
        self.ack_lock = threading.Lock

    def _init_socket(self):
        self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server_socket.bind(self.addr, self.port)

    def selective_repeat(self, bytes_data: dict):
        no_of_packets = len(bytes_data)
        time_stamps = {}
        # for i in range(min(no_of_packets, self.window_size)):
        #     self.curr_download.[self.nextpckt] = bytes_data[self.nextpckt]
        #     self.nextpckt += 1
        # self.nextpckt = 1
        self.acked = {key: False for key in bytes_data}
        last_packet_ind = self.seq + len(bytes_data)
        for data_idx in sorted(bytes_data.keys()):
            self.curr_download[data_idx] = data_idx.to_bytes(length=5, byteorder="big") + bytes_data[data_idx]
        while True:
            if not self.expct_ack:
                self.send_list()
            self.recieve_Acks()
            if not self.curr_download:
                break

    # def selective_repeat_sender(self, something_to_send):  # todo decide about
    #     # parameters
    #     """
    #     sending the file in selective-repeat reno combination
    #     :param something_to_send: which part of the file to send
    #     :return:
    #     """
    #
    #     # init queue and timestamps
    #     packets_number = len(something_to_send)
    #     time_stamps = {}
    #     packets_queue = deque()
    #     for i in range(min(packets_number, self.window_size)):
    #         packets_queue.append(something_to_send[self.nextpckt])
    #         self.nextpckt += 1
    #     self.acked = {key: False for key in something_to_send}
    #     last_packet_ind = self.seq + len(something_to_send)
    #
    #     # send first round
    #     for i in range(len(packets_queue)):
    #         ind = packets_queue.pop()
    #         self.send_packet(something_to_send, ind)
    #         time_stamps[i] = time.clock()
    #         packets_queue.append(ind)
    #         self.recieve_Acks()
    #
    #     # continue sending
    #     self.recieve_Acks()  # todo can handle several?
    #     while len(packets_queue) != 0:
    #         # todo wait(delay)
    #         i = packets_queue.pop()
    #         if not self.acked[i]:
    #             if abs(time.clock() - time_stamps[i]) > self.timeout:
    #                 # todo checkv units of time
    #                 self.send_packet(i)
    #                 time_stamps[i] = time.clock()
    #             packets_queue.append(i)
    #         self.recieve_Acks()
    #
    #         # advanced window
    #         if self.acked[self.seq]:
    #             self.seq += 1
    #             if self.nextpckt <= last_packet_ind:
    #                 packets_queue.append(something_to_send[self.nextpckt])
    #                 self.nextpckt += 1

    def send_list(self):
        while len(self.expct_ack) < self.window_size:
            self.send_packet(self.curr_download[self.nextpckt])
            self.nextpckt += 1
            self.expct_ack.append(self.nextpckt)

    def send_packet(self, packet_data):
        self.udp_server_socket.sendto(packet_data, (self.addr, self.port))
        self.expct_ack.append(self.nextpckt)

    def recieve_Acks(self):
        while True:
            try:
                data, address = self.udp_server_sock.recvfrom(5)
                idx = data[:5]
                ack_rcv = int(int.from_bytes(idx, byteorder="big"))
                self.acked[ack_rcv] = True
                if self.expct_ack.index(ack_rcv) is None:
                    continue
                right_seq = self.expct_ack.pop(0)
                if ack_rcv != right_seq:
                    self.send_packet(self.curr_download[right_seq])
                    self.expct_ack.append(right_seq)
                self.expct_ack.pop(ack_rcv)
                self.curr_download.pop(ack_rcv)
                if not self.expct_ack:
                    pass  # congestion control increase window
            finally:
                if self.expct_ack:
                    pass  # congestion control decrease window
                break

    def selective_repeat_server(self):

        udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_sock.bind(self.addr, self.port)
        # packet limit sending everytime
        packet_limit = 4
        # checking if somebody is connected to the udp
        is_connected = False
        while True:
            # checking if somebody connected
            if not is_connected:
                try:
                    data, address = udp_server_sock.recvfrom(2048)
                    is_connected = True
                except:
                    pass
            # somebody is connected
            else:
                while len(self.expct_ack) < packet_limit and self.curr_download.get(
                        self.nextpckt) is not None:
                    udp_server_sock.sendto(self.curr_download[self.nextpckt], address)
                    self.expct_ack.append(self.nextpckt)
                    self.nextpckt += 1
                try:
                    print(self.expct_ack)
                    # getting the number of the packet from the client(ack) and removing from the dict
                    data, address = self.udp_server_sock.recvfrom(5)
                    print(int(data.decode()))
                    if self.expct_ack.index(int(data.decode())) is None:
                        continue
                    ack_idx = self.expct_ack.index(int(data.decode()))
                    for packet_num in self.expct_ack:
                        if packet_num == int(data.decode()):
                            # self.expct_ack.pop(0)
                            self.download_now.pop(packet_num)
                            break
                        udp_server_sock.sendto(self.curr_download[packet_num], address)
                        self.expct_ack.append(packet_num)
                        # self.expct_ack.pop(0)
                    while ack_idx > -1:
                        self.expct_ack.pop(0)
                        ack_idx -= 1
                    # data = number of packet
                except:
                    for packet_num in self.expct_ack:
                        udp_server_sock.sendto(self.download_now[packet_num], address)

                # # how many packets we sent
                # index_to_send = 0
                # # sending the packets until the limit the we set
                # for packet in self.download_now.values():
                #     udp_server_sock.sendto(packet, address)
                #     index_to_send += 1
                #     if index_to_send == packet_limit:
                #         break
                # # how many packets the client received
                # index_to_recv = 0
                # while index_to_recv < index_to_send:
                #     udp_server_sock.settimeout(1)
                #     try:
                #         # getting the number of the packet from the client(ack) and removing from the dict
                #         data, address = udp_server_sock.recvfrom(5)
                #         # data = number of packet
                #         self.download_now.pop(int(data.decode()))
                #         index_to_recv += 1
                #     except timeout:
                #         index_to_recv += 1
                # we send all the file to the client and waiting for him to confirm
                while len(self.download_now) == 0:
                    is_connected = False
                    udp_server_sock.settimeout(0.5)
                    try:
                        udp_server_sock.sendto("Done!".encode(), address)
                        data, address = udp_server_sock.recvfrom(5)
                        if data.decode() == 'finally':
                            self.can_download = True
                            break
                    except:
                        pass
