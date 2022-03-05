import socket
import sys
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
        self.last_packet_ind = 0
        self.expct_ack = []
        self.window_size = 4
        # self.window = tuple(1, 1)
        self.timeout = 4
        # self.sum_of_packets = math.ceil(self.size_of_file / 2022)
        self.udp_server_socket = None

    def run(self, bytes_data: dict):
        self._init_socket(bytes_data)
        self.selective_repeat()
        self.close()

    def _init_socket(self, bytes_data: dict):
        try:
            self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_server_socket.bind((self.addr, self.port))
        finally:
            while True:
                try:
                    msg, addr = self.udp_server_socket.recvfrom(5)
                    self.port = addr[1]
                    self.last_packet_ind = 0
                    self.nextpckt = sys.maxsize
                    for key in bytes_data.keys():
                        self.last_packet_ind = max(self.last_packet_ind, key)
                        self.nextpckt = min(self.nextpckt, key)
                    self.acked = {key: False for key in bytes_data}

                    for data_idx in sorted(bytes_data.keys()):
                        self.curr_download[data_idx] = data_idx.to_bytes(length=5, byteorder="big") + bytes_data[
                            data_idx]
                    break
                except Exception as e:
                    print(e)
                    pass

    def selective_repeat(self):
        while True:
            try:
                while len(self.expct_ack) < self.window_size and self.nextpckt <= self.last_packet_ind:
                    self.send_packet(self.curr_download[self.nextpckt])
                    self.nextpckt += 1
                    self.seq += 1
            except ConnectionError:
                break

            self.recieve_Ack()
            if not self.curr_download:
                break

    def send_packet(self, packet_data):
        self.udp_server_socket.sendto(packet_data, (self.addr, self.port))
        self.expct_ack.append(self.nextpckt)

    def recieve_Ack(self):
        try:
            self.udp_server_socket.settimeout(2.2)
            data, address = self.udp_server_socket.recvfrom(5)
            idx = data[:5]
            ack_rcv = int(int.from_bytes(idx, byteorder="big"))
            self.acked[ack_rcv] = True
        except socket.timeout as error:
            print(error)
            if self.window_size > 4:
                self.window_size = 4
            else:
                self.window_size = 2
            for key in self.expct_ack:
                try:
                    self.udp_server_socket.sendto(self.curr_download[key], (self.addr, self.port))
                except Exception as e:
                    print(e)
            return
        except socket.error as error:
            print(error)
            while len(self.expct_ack):
                test = self.expct_ack.pop(0)
                self.curr_download.pop(test)

        try:
            self.expct_ack.index(ack_rcv)
            while True:
                right_seq = self.expct_ack.pop(0)
                if ack_rcv != right_seq:
                    self.udp_server_socket.sendto(self.curr_download[right_seq], (self.addr, self.port))
                    self.expct_ack.append(right_seq)
                    if self.window_size > 2:
                        self.window_size -= 1
                else:
                    self.curr_download.pop(ack_rcv)
                    if self.window_size < 32:
                        self.window_size *= 2
                    else:
                        self.window_size += 2
                    return
        except:
            pass

    def close(self):
        print("closed")
        self.udp_server_socket.close()
