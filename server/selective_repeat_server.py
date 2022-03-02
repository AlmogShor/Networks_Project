import socket
import time


def getClocks(num_of_clocks):
    clocks = [time.clock()]*num_of_clocks
    for(c in clocks){
        c.
    }
    return clocks

class selective_repeat:
    @classmethod
    def __init__(self,addr,port):
        self.addr=addr
        self.port=port
        self.seq = 0
        self.curr_download = 0
        self.nextpckt = 1
        self.timeout_clockes = getClocks(4);

    def selective_repeat_server(self, address, port):
        address_server = (address, port)
        udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_sock.bind(address_server)
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
                except timeout:
                    pass
            # somebody is connected
            else:
                while len(self.exp_ack) < packet_limit and self.curr_download.get(self.nextpckt) is not None:
                    udp_server_sock.sendto(self.curr_download[self.nextpckt], address)
                    self.exp_ack.append(self.nextpckt)
                    self.nextpckt += 1
                try:
                    print(self.exp_ack)
                    # getting the number of the packet from the client(ack) and removing from the dict
                    data, address = udp_server_sock.recvfrom(5)
                    print(int(data.decode()))
                    if self.exp_ack.index(int(data.decode())) is None:
                        continue
                    ack_idx = self.exp_ack.index(int(data.decode()))
                    for packet_num in self.exp_ack:
                        if packet_num == int(data.decode()):
                            # self.exp_ack.pop(0)
                            self.download_now.pop(packet_num)
                            break
                        udp_server_sock.sendto(self.download_now[packet_num], address)
                        self.exp_ack.append(packet_num)
                        # self.exp_ack.pop(0)
                    while ack_idx > -1:
                        self.exp_ack.pop(0)
                        ack_idx -= 1
                    # data = number of packet
                except timeout:
                    for packet_num in self.exp_ack:
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
                        if data.decode() == 'sabab':
                            self.can_download = True
                            break
                    except timeout:
                        pass
