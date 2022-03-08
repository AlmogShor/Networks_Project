from scapy import all as scp
import argparse
import threading
from collections import deque
import time
import loges as Logger

MSS = 1400  # final
RETRANSMIT_TIMEOUT = 4.0  # in seconds final


class reno_server:
    def __init__(self, user_name, server_ip="127.0.0.1", client_ip="127.0.0.1", server_port=50100, client_port=50101, file_dl='x', **kwargs):
        # you can add role if it a sender or reciever IRL
        self.seq_cnt = 0
        self.next_seq = 1
        self.ack = 1
        self.user_name = user_name
        self.received_packets = deque()
        self.outstanding_segments = set()

        self.cwnd = 1 * MSS
        self.ssthresh = 64 * 1024  # 64KB as Amit requests
        # self.dupack = 0
        # self.state = "slow_start"
        # # see [RFC 6298] on how the retransmission timer works
        # self.retransmission_timer = None

        # self.role = role  # sender or receiver IRL
        self.log_cache = None

        self.src_addr = server_ip
        self.dest_addr = client_ip
        self.client_port = client_port
        self.server_port = server_port
        self.role = 'sender'
        self.bytes_data = file_dl
        self.file_index = 0
        self.limit = None

        # stop the sender after seq_no exceeding this limit ***need to do it through the GUI***
        if 'limit' in kwargs:
            self.limit = kwargs['limit']

        # list of time logs for plotting
        self.seq_log, self.ack_log = [], []

    def start_sender(self):
        # self.xprint("retransmission timeout: %.1fs" % RETRANSMIT_TIMEOUT)
        last_log_time = 0
        while True:
            if self.state == "slow_start" and self.cwnd >= self.ssthresh:
                self.state = "congestion_avoidance"
            if self.next_seq - self.seq_cnt - 1 < self.cwnd:
                self.send()
            if self.receive() == 'tear_down':
                self.state = 'tear_down'
                break
            if self.state != 'fin_sent':
                self.timeout()

            # send FIN when data sent over pre-specified limit
            if self.limit and self.seq_cnt >= self.limit:
                if self.state == 'fin_sent' \
                        and self.retransmission_timer + RETRANSMIT_TIMEOUT < time.time():
                    continue
                self.send_fin()
                self.retransmission_timer = 0
                self.state = 'fin_sent'

    def send(self):
        if self.limit and self.next_seq > self.limit:
            return  # here we should make the stop point for Amit
        packet = scp.IP(src=self.src_addr, dst=self.dest_addr) \
                 / scp.TCP(sport=self.server_port, dport=self.client_port,
                           flags='', seq=self.next_seq) \
                 / self.bytes_data[self.file_index:self.file_index+MSS] # (DUMMY_PAYLOAD)
        scp.send(packet, verbose=0)
        self.next_seq += MSS
        if self.retransmission_timer is None:
            self.retransmission_timer = time.time()
        Logger.info(f"sequence no.[{self.seq_cnt}] sent to [{self.user_name}]")

    def resend(self, event):
        packet = scp.IP(src=self.src_addr, dst=self.dest_addr) \
                 / scp.TCP(sport=self.server_port, dport=self.client_port,
                           flags='', seq=self.seq + 1) \
                 / self.bytes_data[self.file_index:self.file_index+MSS]
        self.retransmission_timer = time.time()
        scp.send(packet, verbose=0)

    def timeout(self):
        if self.retransmission_timer is None:
            return
        elif self.retransmission_timer + RETRANSMIT_TIMEOUT < time.time():
            # on timeout
            self.resend('timeout')
            self.state = "slow_start"
            self.ssthresh = self.cwnd / 2
            self.cwnd = 1 * MSS
            self.dupack = 0

    def receive(self):
        if len(self.received_packets) == 0:
            return
        pkt = self.received_packets.popleft()[0]

        # ack received
        if pkt[scp.TCP].flags & 0x10:  # ACK
            if pkt[scp.TCP].ack - 1 > self.seq_cnt:
                # new ack
                self.seq_cnt = pkt[scp.TCP].ack - 1
                """
                [RFC 6298]
                    (5.3) When an ACK is received that acknowledges new data, 
                restart the retransmission timer so that it will expire after 
                RTO seconds (for the current value of RTO).
                """
                self.retransmission_timer = time.time()  # restart timer
                if self.state == "slow_start":
                    self.cwnd += MSS
                elif self.state == "congestion_avoidance":
                    self.cwnd += MSS * MSS / self.cwnd
                elif self.state == "fast_recovery":
                    self.state = "congestion_avoidance"
                    self.cwnd = self.ssthresh
                self.dupack = 0
            else:
                # duplicate ack
                self.dupack += 1
                """
                On the first and second duplicate ACKs received at a 
                sender, a TCP SHOULD send a segment of previously unsent data 
                per [RFC 3042] provided that the receiver's advertised window 
                allows, the total Flight Size would remain less than or 
                equal to cwnd plus 2*SMSS, and that new data is available 
                for transmission.  Further, the TCP sender MUST NOT change 
                cwnd to reflect these two segments [RFC 3042].
                """
                if self.dupack < 3:
                    self.send()
                elif self.dupack == 3:
                    self.state = "fast_recovery"
                    self.ssthresh = self.cwnd / 2
                    self.cwnd = self.ssthresh + 3 * MSS
                    # retransmit missing packet
                    self.resend('triple-ack')
                elif self.state == "fast_recovery":
                    self.cwnd += MSS
        # fin received
        elif pkt[scp.TCP].flags & 0x1:  # FIN
            if self.role == 'sender' and self.state == 'fin_sent':
                Logger.info(f"Final sequence sent to [{self.user_name}]")
                return 'tear_down'
            if self.role == 'receiver':
                self.send_fin()
                return 'tear_down'
