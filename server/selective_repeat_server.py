import socket
import threading
import time
# from loges import Logger
from collections import deque
import math


class selective_repeat:
    @classmethod
    def __init__(self, addr, port):
        self.acked = {}
        self.addr = '127.0.0.1'
        self.port = port
        self.seq = 0
        self.curr_download = {}
        self.nextpckt = 1
        self.expct_ack = []
        self.window_size = 4
        # self.window = tuple(1, 1)
        self.timeout = 4
        # self.sum_of_packets = math.ceil(self.size_of_file / 2022)
        self.udp_server_socket = None

    def run(self, bytes_data: dict):
        print("start run")
        self._init_socket()
        print("after init")
        self.selective_repeat(bytes_data)
        self.close()

    def _init_socket(self):
        try:
            self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_server_socket.bind((self.addr, self.port))
        finally:

            self.udp_server_socket.settimeout(2)
            try:
                msg, addr = self.udp_server_socket.recvfrom(5)
                print(msg)
                print(addr)
                self.port = addr[1]
            except Exception as e:
                print(e)
                pass

    def selective_repeat(self, bytes_data: dict):
        last_packet_ind = 0
        self.nextpckt = 1000000
        for key in bytes_data.keys():
            last_packet_ind = max(last_packet_ind, key)
            self.nextpckt = min(self.nextpckt, key)
        no_of_packets = len(bytes_data)
        time_stamps = {}
        self.acked = {key: False for key in bytes_data}
        # last_packet_ind = self.seq + no_of_packets
        for data_idx in sorted(bytes_data.keys()):
            self.curr_download[data_idx] = data_idx.to_bytes(length=5, byteorder="big") + bytes_data[data_idx]
        while True:
            print(self.expct_ack)
            try:
                while len(self.expct_ack) < self.window_size and self.nextpckt <= last_packet_ind:
                    self.send_packet(self.curr_download[self.nextpckt])
                    self.nextpckt += 1
                    self.seq += 1
            except ConnectionError:
                break

            self.recieve_Ack()
            if not self.expct_ack:
                if self.window_size < 32:
                    self.window_size *= 2
                else:
                    self.window_size += 2
            elif self.expct_ack:
                self.window_size = math.ceil(self.window_size / 2)

            if not self.curr_download:
                break

    def send_packet(self, packet_data):
        print(packet_data)
        self.udp_server_socket.sendto(packet_data, (self.addr, self.port))
        self.expct_ack.append(self.nextpckt)

    def recieve_Ack(self):
        try:
            self.udp_server_socket.settimeout(1)
            data, address = self.udp_server_socket.recvfrom(5)
            idx = data[:5]
            ack_rcv = int(int.from_bytes(idx, byteorder="big"))
            self.acked[ack_rcv] = True
        except:
            return
        try:
            self.expct_ack.index(ack_rcv)
            right_seq = self.expct_ack.pop(0)
            if ack_rcv != right_seq:
                self.send_packet(self.curr_download[right_seq])
                self.expct_ack.append(right_seq)
            else:
                self.curr_download.pop(ack_rcv)
                return
        except:
            pass
        # self.expct_ack.pop(ack_rcv)

        #     while True:
        #         try:
        #             idx = data[:5]
        #             ack_rcv = int(int.from_bytes(idx, byteorder="big"))
        #             if self.expct_ack.index(ack_rcv) is None:
        #                 continue
        #             right_seq = self.expct_ack.pop(0)
        #             if ack_rcv != right_seq:
        #                 self.send_packet(self.curr_download[right_seq])
        #                 self.expct_ack.append(right_seq)
        #             else:
        #                 self.curr_download.pop(ack_rcv)
        #                 break
        #             # self.expct_ack.pop(ack_rcv)
        #
        #             if not self.expct_ack:
        #                 pass  # congestion control increase window
        #         finally:
        #             if self.expct_ack:
        #                 pass  # congestion control decrease window
        #             break
        # except:
        #     pass

    def close(self):
        self.udp_server_socket.close()
