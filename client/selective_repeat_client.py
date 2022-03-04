import socket
import time


class selective_repeat_client:
    def __init__(self, addr, port):

        self.rcv_seq = 0
        self.server_addr = addr
        self.port = port
        self.sum_of_packets = 0
        self.file_dict = {}
        self.udp_client_socket = None
        # self._init_socket()

    def run(self, length):
        self.rcv_seq = 0
        self.sum_of_packets = length
        data = self._init_socket()
        self.selective_repeat(data)

    # def scnd_run(self, length):
    #     self.rcv_seq = 0
    #     self.sum_of_packets = length
    #     data = self.scnd_init()
    #     self.selective_repeat(data)
    #
    # def scnd_init(self):
    #     while True:
    #         time.sleep(0.01)
    #         try:
    #             data, address = self.udp_client_socket.recvfrom(2027)
    #             return data
    #         except:
    #             pass

    def _init_socket(self):
        self.udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_client_socket.bind((self.server_addr, self.port))  # todo check
        packet = 0
        packet.to_bytes(length=5, byteorder="big")
        while True:
            time.sleep(0.25)
            try:
                self.udp_client_socket.sendto(packet, (self.server_addr, self.port))
                data, address = self.udp_client_socket.recvfrom(2027)

                return data
            except:
                pass

    def selective_repeat(self, data):
        while True:
            idx = data[:5]
            self.file_dict[int(int.from_bytes(idx, byteorder="big"))] = data[5:]
            # send ack
            self.udp_client_socket.sendto(idx, (self.server_addr, self.port))
            self.rcv_seq += 1
            if self.rcv_seq == self.sum_of_packets:
                break
            data, address = self.port.recvfrom(2027)

    def close(self):
        self.udp_client_socket.settimeout(2)
        return self.file_dict
