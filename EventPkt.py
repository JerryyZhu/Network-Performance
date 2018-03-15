# Packet which contains all the necessary information


class EventPkt(object):
    packet_size = 0
    start_time = 0
    end_time = -1
    packet_no = 0
    proc_time
    arrival_time

    def __init__(self, x, packetsize, starttime):
        self.packet_size = packetsize
        self.start_time = starttime
        self.packet_no = x
        self.process_time = 0

    def get_start(self):
        return start_time

    def get_endtime(self):
        return end_time

    def get_arrivaltime(self):
        return arrival_time

    def set_arrivaltime(self, starttime):
        self.arrival_time = startTime

    def set_endtime(self, endtime):
        self.end_time = endtime

    def set_processtime(self, time):
        self.process_time = time

    def get_packet_size(self):
        return self.packet_size

    def set_start_time(self, start_time):
        self.start_time = start_time