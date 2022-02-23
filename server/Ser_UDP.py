import socket
import select
import random
from itertools import imap, chain
from operator import sub

fragment_size = 600  # maybe can be bigger - size in Bytes
window_size = 10
client_list = []  # list of currently clients thats downloading files.


def final_window_packet():
    pass


def send_over_UDP(ip, port):
    pass

