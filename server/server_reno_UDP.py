from scapy import all as scp
import argparse
import threading
from collections import deque
import time
import loges as Logger

MSS = 1400  # final
RETRANSMIT_TIMEOUT = 4.0  # in seconds final


class reno_server:
    def __init__(self, addr, port, user_name, **kwargs):  # you can add role if it a sender or reciever IRL
        self.seq_cnt = 0
        self.next_seq = 1
        self.ack = 1
        self.user_name= user_name
        self.received_packets = deque()
        self.outstanding_segments = set()

        self.cwnd = 1 * MSS
        self.ssthresh = 64 * 1024  # 64KB as Amit requests
        self.dupack = 0
        self.state = "slow_start"
        # see [RFC 6298] on how the retransmission timer works
        self.retransmission_timer = None

        # self.role = role  # sender or receiver IRL
        self.log_cache = None

        self.src_addr = '127.0.0.1'
        self.dest_addr = addr
        self.client_port = port

        self.limit = None

        # stop the sender after seq_no exceeding this limit ***need to do it through the GUI***
        if 'limit' in kwargs:
            self.limit = kwargs['limit']

        # list of time logs for plotting
        self.seq_log, self.ack_log = [], []

    def start_sender(self):
        self.xprint("retransmission timeout: %.1fs" % RETRANSMIT_TIMEOUT)
        last_log_time = 0
        while True:
            if self.state == "slow_start" and self.cwnd >= self.ssthresh:
                self.state = "congestion_avoidance"
            if self.next_seq - self.seq - 1 < self.cwnd:
                self.send()
            if self.receive() == 'tear_down':
                self.state = 'tear_down'
                break
            if self.state != 'fin_sent':
                self.timeout()

            # send FIN when data sent over pre-specified limit
            if self.limit and self.seq >= self.limit:
                if self.state == 'fin_sent' \
                        and self.retransmission_timer + RETRANSMIT_TIMEOUT < time.time():
                    continue
                self.send_fin()
                self.retransmission_timer = 0
                self.state = 'fin_sent'

    def send(self):
        if self.limit and self.next_seq > self.limit:
            return  # here we should make the stop point for Amit

        self.next_seq += MSS
        if self.retransmission_timer is None:
            self.retransmission_timer = time.time()
        Logger.info(f"sequence no.[{self.seq_cnt}] sent to [{self.user_name}]")


    def send_ack(self, ack_no):
        # update ack log
        packet = scp.IP(src=self.src_ip, dst=self.dst_ip) \
                 / scp.TCP(sport=self.src_port, dport=self.dst_port,
                           flags='A', ack=ack_no)
        scp.send(packet, verbose=0)
        self.ack_log.append((time.time() - self.base_time, ack_no))

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