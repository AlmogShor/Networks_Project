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
        self.user_name = user_name
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

    def post_receive(self, pkt, status):
        # called after a data segment is received
        # subclass overwrites this function to implement attacks
        self.send_ack(self.ack)

    def receive(self):
        if len(self.received_packets) == 0:
            return
        pkt = self.received_packets.popleft()[0]

        # data packet received
        if pkt[scp.TCP].flags == 0:
            # update seq log
            self.seq_log.append((time.time() - self.base_time, pkt[scp.TCP].seq))
            if pkt[scp.TCP].seq == self.ack:
                status = 'new'
                self.ack += MSS
                while self.ack in self.outstanding_segments:
                    self.outstanding_segments.remove(self.ack)
                    self.ack += MSS
            elif pkt[scp.TCP].seq > self.ack:
                # a future packet (queue it)
                status = 'future'
                self.outstanding_segments.add(pkt[scp.TCP].seq)
            else:
                status = 'duplicate'
            self.post_receive(pkt, status)
        # ack received
        elif pkt[scp.TCP].flags & 0x10:  # ACK
            if pkt[scp.TCP].ack - 1 > self.seq:
                # new ack
                self.seq = pkt[scp.TCP].ack - 1
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
                [RFC 5681]
                    On the first and second duplicate ACKs received at a 
                sender, a TCP SHOULD send a segment of previously unsent data 
                per [RFC 3042] provided that the receiver's advertised window 
                allows, the total Flight Size would remain less than or 
                equal to cwnd plus 2*MSS, and that new data is available 
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
            self.send_fin()
            return 'tear_down'
