import sys
from SourceModel import *
from collections import deque
import random
import Queue


PACKET_SIZE_MEAN = 1250
FILENAME = 'trace.txt'
LINK_SPEED = 1250
DEBUG = True

class Event:
    # Input parameters
    N_PKTS = None
    LAMBDA = None
    RATE = LINK_SPEED # 10 GBPS, bytes per us

    # Server
    current_packet = None
    server_queue = None
    current_packet = None
    current_queue_size = 0
    source_queue = None


    # Measurement parameter
    total_cust = 0
    total_sojourn = 0

    # Time
    cur_time = 0.0
    cur_departure_time = 0.0
    cur_proc = 0.0


    def __init__(self, numPackets, packet_size_mean):
        self.N_PKTS = numPackets
        self.LAMBDA = packet_size_mean


    def start_sim(self):
        self.server_queue = Queue.Queue()
        for x in range(0,self.N_PKTS):
            incoming_packet = self.sourceModel.generate_packet()
            self.handle_arrival(incoming_packet, self.server_queue)

        # Process packets still left in the server queue
        while self.server_queue.empty() == False:
            packet = self.server_queue.get()
            # get current time, this is when the packet starts processing
            # calculate departure time, figure out sojourn time
            # announce departure
            # departure time is now current time

            #
            self.cur_proc = self.get_process_time(packet)
            self.cur_departure_time = self.cur_proc + self.cur_time
            self.cur_time = self.cur_departure_time
            self.output_departure(packet, self.calculate_sojourn(packet,self.cur_time))


    def handle_arrival(self,incoming,server_queue):

        inc_arrival_time = incoming.get_arrivaltime()
        # Case 1 First Packet Ever
        if self.current_packet is None:
            self.current_packet = incoming
            self.cur_time = inc_arrival_time
            self.cur_proc = self.get_process_time(incoming)
            print("current:" + str(self.cur_time) + " | " + str(self.cur_proc))

            self.cur_departure_time = self.cur_time + self.cur_proc
            print("departure time:" + str(self.cur_departure_time))

            self.output_arrival(incoming)
            self.total_sojourn += self.cur_proc
            if DEBUG:
                # print('first packet')
                print("packet {}: | arrival: {} | process: {} | departure: {} | cur: {}|".format(self.current_packet.get_packetno(),
                                                                             self.current_packet.get_arrivaltime(), self.cur_proc,
                                                                             self.cur_departure_time, self.cur_time))

        else:
            # Case 2 Queue not empty
            while server_queue.empty() == False:
                # Incoming packet arrives later than the time current packet leaves
                # If server queue not empty then check if the next packet finishes earlier
                if inc_arrival_time > self.cur_departure_time:
                    # The current packet will leave
                    self.cur_time = self.cur_departure_time
                    self.output_departure(self.current_packet, self.calculate_sojourn(self.current_packet,self.cur_time))
                    if self.current_queue_size > 0:
                        self.current_queue_size -= 1
                    self.current_packet = server_queue.get()
                    # self.cur_time = self.current_packet.get_arrivaltime()
                    self.cur_departure_time = self.calculate_departure(self.current_packet, self.cur_time)
                    self.cur_proc = self.get_process_time(self.current_packet)
                    print("cur packet {}: | cur arrival: {} | cur process: {} | cur departure: {} | cur: {}|".format(
                        self.current_packet.get_packetno(),
                        self.current_packet.get_arrivaltime(), self.cur_proc, self.cur_departure_time,
                        self.cur_time))

                # If does not finish earlier than next packet, add incoming to queue
                else:
                    # Announce arrival
                    self.cur_time = inc_arrival_time
                    self.output_arrival(incoming)
                    # Increase queue size
                    self.current_queue_size += 1
                    server_queue.put(incoming)
                    print("packet {}: | arrival: {} | process: {} | departure: {} | cur: {}|".format(
                        self.current_packet.get_packetno(),
                        self.current_packet.get_arrivaltime(), self.cur_proc, self.cur_departure_time,
                        self.cur_time))
                    return

            # Case 3 Queue empty
            if inc_arrival_time > self.cur_departure_time:
                # Current packet leaves, incoming becomes new current
                self.cur_time = self.cur_departure_time
                self.output_departure(self.current_packet, self.calculate_sojourn(self.current_packet, self.cur_time))
                if self.current_queue_size > 0:
                    self.current_queue_size -= 1
                self.current_packet = incoming
                self.cur_time = inc_arrival_time
                self.cur_proc = self.get_process_time(incoming)
                self.cur_departure_time = self.cur_time + self.cur_proc
                self.output_arrival(incoming)
                self.current_queue_size += 1
                print("packet {}: | arrival: {} | process: {} | departure: {} | cur: {}|".format(
                    self.current_packet.get_packetno(),
                    self.current_packet.get_arrivaltime(), self.cur_proc, self.cur_departure_time,
                    self.cur_time))

            # Current packet still processing
            else:
                server_queue.put(incoming)
                self.cur_time = inc_arrival_time
                self.output_arrival(incoming)
                self.current_queue_size += 1


    def get_process_time(self,incoming_pkt):
        # if DEBUG:
        #     print("size "+ str(incoming_pkt.get_packet_size()) + "| rate: " + str(self.RATE) )
        #     print(str(incoming_pkt.get_packet_size()/self.RATE))
        return incoming_pkt.get_packet_size()/self.RATE

    def output_arrival(self,incoming_pkt):
        # [3749.00]: pkt 2748 arrives and finds 38 packets in the queue
        print("[{}]: pkt {} and finds {} in the queue").format(self.cur_time,
                                                              incoming_pkt.get_packetno(),
                                                              self.current_queue_size)
        # TODO update array with P[0..10]

        # TODO update queue size total ie total_customers

    def output_departure(self,packet,sojourn):
        # [4638.00]: pkt 6102 departs having spent 243.00 us in the system
        print("[{}] pkt {} departs having spent {} us in the system".format(
            self.cur_time, packet.get_packetno(), sojourn
        ))

    def calculate_sojourn(self, current_packet, current_time):
        sojourn = current_time - current_packet.get_arrivaltime()
        self.total_sojourn += sojourn
        return sojourn

    def calculate_departure(self, packet, current_time):
        return (current_time + self.get_process_time(packet))

    def generateSource(self):
        source = SourceModel(self.N_PKTS,int(sys.argv[2]),PACKET_SIZE_MEAN)
        self.sourceModel = source
        self.source_queue = source.generate_packets()

    def read_from_file(self):
        q = queue.Queue()
        last_line = None

        with open(FILENAME) as f:
            for line in f:
                if not last_line == None:
                    data = line.split()
                last_line = line


def main():
    if len(sys.argv) < 3:
        print("Usage: {} npkts lambda".format(sys.argv[0]))

    # for x in range(len(sys.argv)):
    #     print(sys.argv[x])
    # #
    EventHandler = Event(int(sys.argv[1]),int(sys.argv[2]))
    # print(sys.argv[1])
    EventHandler.generateSource()
    EventHandler.start_sim()


if __name__ == '__main__':
    main()
