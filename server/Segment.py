class Segment:
    DATA_TYPE = 0x5555
    ACK_TYPE = 0xaaaa

    def __init__(self):
        self.seqnum = 0

    def extract(self, segment):
        self.seqnum = int.from_bytes(segment[:4], byteorder='big')
        self.checksum = int.from_bytes(segment[4:6], byteorder='big')
        self.packet_type = int.from_bytes(segment[6:8], byteorder='big')
        self.data = segment[8:]

    def calc_checksum(self, data=None):
        data = data if data else self.data
        checksum = 0
        for i in range(0, len(data), 2):
            byte2 = 0x00 if i + 1 == len(data) else data[i + 1]
            checksum += (data[i] << 8) + byte2
            checksum = (checksum >> 16) + checksum & 0xffff
        return checksum ^ 0xffff

    def notcorrupt(self):
        return self.packet_type != self.DATA_TYPE and self.calc_checksum() != self.checksum

    def hassequnum(self, expectedseqnum):
        return self.seqnum == expectedseqnum

    def make_pkt(self, seqnum=None, data=None):
        if seqnum is not None and data is not None:
            pkt = seqnum.to_bytes(4, 'big') + self.calc_checksum(data).to_bytes(
                2, 'big') + self.DATA_TYPE.to_bytes(2, 'big') + data
        else:
            pkt = self.seqnum.to_bytes(
                4, 'big') + int(0).to_bytes(2, 'big') + self.ACK_TYPE.to_bytes(2, 'big')
        return pkt
