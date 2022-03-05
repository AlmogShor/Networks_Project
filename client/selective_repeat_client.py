import socket
import time


class selective_repeat_client:
    def __init__(self, addr, port, filename):

        self.rcv_seq = 0
        self.server_addr = '127.0.0.1'
        self.port = port
        self.sum_of_packets = 0
        self.file_dict = {}
        self.udp_client_socket = None
        self.filename = filename

    def run(self, length):
        print("start run")
        self.rcv_seq = 0
        self.sum_of_packets = length
        print(length)
        data = self._init_socket()
        self.selective_repeat(data)
        self.close()
        self.write_file(self.filename, self.file_dict)
        print("done here")

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
        try:
            self.udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.udp_client_socket.bind((self.server_addr, 51000))  # todo check
        finally:
            time.sleep(0.25)
            try:
                print("insert try init")
                self.udp_client_socket.sendto("ack".encode(), (self.server_addr, self.port))
                data, address = self.udp_client_socket.recvfrom(512)
                print(data)

                return data
            except:
                print("except")

    def selective_repeat(self, data):
        while True:
            print(data)
            idx = data[:5]
            indx = int(int.from_bytes(data[:5], byteorder="big"))
            try:
                self.file_dict[indx]
            except Exception as e:
                print(e)
                self.file_dict[indx] = data[5:]
                self.rcv_seq += 1
            # send ack
            self.udp_client_socket.sendto(idx, (self.server_addr, self.port))
            if self.rcv_seq == self.sum_of_packets:
                print("here")
                break
            data, address = self.udp_client_socket.recvfrom(512)

    def write_file(self, filename, bytes_data):
        """ write bytes data to the file
            >>> @param:filename:    -> name of the file
            >>> @param:bytes_data:  -> data to be written, in the form of bytes
        """
        sorted(bytes_data.keys())
        with open(filename, "ab") as f:
            for keys, value in bytes_data.items():
                f.write(value)

    def close(self):
        self.udp_client_socket.close()
        print("success")
        return self.file_dict
