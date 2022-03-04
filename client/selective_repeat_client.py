import socket
import time


class selective_repeat_client:
    def __init__(self, addr, port, length):

        self.rcv_seq = 0
        self.server_addr = addr
        self.port = port
        self.sum_of_packets = length
        self.file_dict = {}
        self.udp_client_socket = None
        # self._init_socket()

    def run(self):
        data = self._init_socket()
        self.selective_repeat(data)

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

    def selective_repeat_reciever(self):
        while True:
            # when getting "Done!" all the file finished to download
            if message.decode() == 'Done!':
                self.udp_client_socket.settimeout(5)
                try:
                    # self.udp_client_socket.sendto('finally'.encode(), (serverip, port))
                    message, address = self.udp_client_socket.recvfrom(2048)
                finally:
                    break


            # when the file didn't finished to downloading
            else:
                message, address = self.udp_client_socket.recvfrom(2048)
                index = message[:5]
                # sending the index of the packet that received(ack)
                self.udp_client_socket.sendto(index, (self.se, self.port_server))
                packet = message[5:]
                # saving the file into the dict
                self.file_dict[int(index.decode())] = packet
                message, address = self.udp_client_socket.recvfrom(2048)

    @classmethod
    def selective_repeat_client(self, serverip="127.0.0.1", port=51000, finished=False):
        udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_client.settimeout(2)
        while True:
            try:
                start = 'start'
                # sending to the server to let him know that the client is ready for downloading
                udp_client.sendto(start.encode(), (serverip, port))
                message, address = udp_client.recvfrom(2048)
                break
            except:
                pass
        udp_client.settimeout(100)
        while True:
            # when getting "Done!" all the file finished to download
            if message.decode() == 'Done!':
                udp_client.settimeout(5)
                try:
                    udp_client.sendto('finally'.encode(), (serverip, port))
                    message, address = udp_client.recvfrom(2048)
                except:
                    break
            # when the file didn't finished to downloading
            else:
                index = message[:5]
                # sending the index of the packet that received(ack)
                udp_client.sendto(index, (self.se, self.port_server))
                packet = message[5:]
                # saving the file into the dict
                self.file[int(index.decode())] = packet
                message, address = udp_client.recvfrom(2048)
        if finished == 'yes':
            # converting the dict back to a file
            self.dict_to_file()
