import signal
import socket
import sys
import threading
import time

import Segment


class Timer:
    def __init__(self, seconds=0.01):
        self.seconds = seconds

    def handle_timeout(self, signum, frame):
        global base, nextseqnum
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
        if base != nextseqnum:
            print('Timeout, sequence number = ' + str(base))
        for seqnum in range(base, nextseqnum):
            udt_send(seqnum)

    def Timeout(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)

    def start_timer(self):
        signal.setitimer(signal.ITIMER_REAL, self.seconds)

    def stop_timer(self):
        signal.alarm(0)


def buffer_data(fName, MSS):
    buffer = []
    seg = Segment.Segment()
    try:
        with open(fName, 'rb') as f:
            data = f.read(MSS)
            seqnum = 0
            while data:
                pkt = seg.make_pkt(seqnum, data)
                buffer.append(pkt)
                data = f.read(MSS)
                seqnum += 1
    except IOError:
        print(fName + ' does not exists')
    return buffer


def udt_send(seqnum):
    s.sendto(buffer[seqnum], (host, port))


def rdt_send():
    global base, nextseqnum, timer
    while True:
        if nextseqnum < min(len(buffer), base + N):
            udt_send(nextseqnum)
            if (base == nextseqnum):
                timer.start_timer()
            nextseqnum += 1
        if nextseqnum >= len(buffer):
            break


def rdt_rcv():
    global base, nextseqnum, timer
    seg = Segment.Segment()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 65534))
    while True:
        segment, addr = s.recvfrom(65535)
        if segment:
            seg.extract(segment)
            base = seg.seqnum + 1
            if (base == nextseqnum):
                timer.stop_timer
            else:
                timer.start_timer


def main():
    global port, timer, N, base, nextseqnum, buffer, s, host
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    base = 0  # base
    nextseqnum = 0  # next sequence number
    host = socket.gethostbyname(sys.argv[1])
    port = int(sys.argv[2])
    fName = sys.argv[3]
    N = int(sys.argv[4])
    MSS = int(sys.argv[5])

    buffer = buffer_data(fName, MSS)
    timer = Timer()
    timer.Timeout()
    t1 = threading.Thread(target=rdt_rcv)
    t1.start()
    rdt_send()
    t1.join()
    timer.stop_timer()
    s.close()


if __name__ == '__main__':
    main()
