import socket
import time
from collections import deque
import math

class selective_repeat_client:
    def __init__(self):

        self.file_dict = {}
        self.udp_client_socket = None
        self._init_socket()

    def _init_socket(self):
        self.udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_client_socket.bind(self.addr, self.port) # todo check


    def selective_repeat_reciever(self):
        while True:
            # when getting "Done!" all the file finished to download
            if message.decode() == 'Done!':
                self.udp_client_socket.settimeout(5)
                try:
                    self.udp_client_socket.sendto('finally'.encode(), (serverip, port))
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
