import random
import sys
from socket import *

import Segment


def random_drop():
    return random.random() <= p


def udt_send(sndpkt, ip):
    s = socket(AF_INET, SOCK_DGRAM)
    s.sendto(sndpkt, (ip, 65534))
    s.close()


def rdt_rcv(port, fName):
    expectedseqnum = 0
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind((gethostbyname(gethostname()), port))

    f = open(fName, 'wb')

    while True:
        seg = Segment.Segment()
        rcvpkt, address = s.recvfrom(65535)
        seg.extract(rcvpkt)
        if random_drop():
            print('Packet loss, sequence number = ' + str(seg.seqnum))
        else:
            if seg.notcorrupt and seg.hassequnum(expectedseqnum):
                f.write(seg.data)
                udt_send(seg.make_pkt(), address[0])
                expectedseqnum += 1


if __name__ == '__main__':
    port = int(sys.argv[1])
    fName = sys.argv[2]
    p = float(sys.argv[3])
    rdt_rcv(port, fName)
