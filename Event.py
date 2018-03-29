import sys
from SourceModel import *
from collections import deque
import random
import Queue
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import numpy as np



PACKET_SIZE_MEAN = 1250
FILENAME = 'small_trace.txt'
LINK_SPEED = 1250
DEBUG = True
P = {}
MAX_QUEUE_SIZE = 0
big_array = []
TOTAL_CUST = 0



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
    global TOTAL_CUST


    # Measurement parameter
    total_cust = 0
    total_sojourn = 0
    total_packets = 0

    # Time
    cur_time = 0.0
    cur_departure_time = 0.0
    cur_proc = 0.0


    def __init__(self, numPackets, packet_size_mean):
        self.N_PKTS = numPackets
        self.LAMBDA = packet_size_mean


    def start_sim(self):
        global TOTAL_CUST
        print("called start_sim")
        self.server_queue = Queue.Queue()
        while not self.source_queue.empty():
            incoming_packet = self.sourceModel.generate_packet()
            self.handle_arrival(incoming_packet, self.server_queue)
            # print(x)
        print("out of while loop")
        # Process packets still left in the server queue
        while self.server_queue.empty() == False:
            packet = self.server_queue.get()
            # get current time, this is when the packet starts processing
            # calculate departure time, figure out sojourn time
            # announce departure
            # departure time is now current time

            self.current_packet = packet
            self.cur_proc = self.get_process_time(packet)
            self.cur_departure_time = self.cur_proc + self.cur_time
            self.cur_time = self.cur_departure_time
            if DEBUG:
                print("packet {}: | arrival: {} | process: {} | departure: {} | cur: {}|".format(
                    self.current_packet.get_packetno(),
                    self.current_packet.get_arrivaltime(), self.cur_proc, self.cur_departure_time,
                    self.cur_time))

            self.output_departure(packet, self.calculate_sojourn(packet,self.cur_time))

        total_sojourn_time = self.total_sojourn
        total_customers = self.total_cust
        TOTAL_CUST = self.total_cust
        # print(int(total_customers))
        # print(int(total_sojourn_time))
        # print("all done")


    def handle_arrival(self,incoming,server_queue):

        self.total_packets += 1
        inc_arrival_time = incoming.get_arrivaltime()
        # Case 1 First Packet Ever
        if self.current_packet is None:
            self.current_packet = incoming
            self.cur_time = inc_arrival_time
            self.cur_proc = self.get_process_time(incoming)

            self.cur_departure_time = self.cur_time + self.cur_proc
            if DEBUG:
                print("current:" + str(self.cur_time) + " | " + str(self.cur_proc))
                print("departure time:" + str(self.cur_departure_time))

            self.output_arrival(incoming)
            self.total_sojourn += self.cur_proc
            if DEBUG:
                # print('first packet')
                print("packet {}: | arrival: {} | process: {} | departure: {} | cur: {}|".format(self.current_packet.get_packetno(),
                                                                             self.current_packet.get_arrivaltime(), self.cur_proc,
                                                                             self.cur_departure_time, self.cur_time))
                print("Queue size is{}".format(self.current_queue_size))
        else:
            # Case 2 Queue not empty
            while server_queue.empty() == False:
                # Incoming packet arrives later than the time current packet leaves
                # If server queue not empty then check if the next packet finishes earlier
                if inc_arrival_time >= self.cur_departure_time:
                    # The current packet will leave
                    self.cur_time = self.cur_departure_time
                    self.output_departure(self.current_packet, self.calculate_sojourn(self.current_packet,self.cur_time))
                    if self.current_queue_size > 0:
                        self.current_queue_size -= 1
                        print("Queue size is{}".format(self.current_queue_size))
                    self.current_packet = server_queue.get()
                    # self.cur_time = self.current_packet.get_arrivaltime()
                    self.cur_departure_time = self.calculate_departure(self.current_packet, self.cur_time)
                    self.cur_proc = self.get_process_time(self.current_packet)
                    if DEBUG:
                        print("cur packet {}: | cur arrival: {} | cur process: {} | cur departure: {} | cur: {}|".format(
                            self.current_packet.get_packetno(),
                            self.current_packet.get_arrivaltime(), self.cur_proc, self.cur_departure_time,
                            self.cur_time))
                        print("Queue size is{}".format(self.current_queue_size))

                # If does not finish earlier than next packet, add incoming to queue
                else:
                    # Announce arrival
                    self.cur_time = inc_arrival_time
                    self.output_arrival(incoming)
                    # Increase queue size
                    self.current_queue_size += 1
                    server_queue.put(incoming)
                    self.total_cust += self.current_queue_size
                    if DEBUG:
                        print("packet {}: | arrival: {} | process: {} | departure: {} | cur: {}|".format(
                            self.current_packet.get_packetno(),
                            self.current_packet.get_arrivaltime(), self.cur_proc, self.cur_departure_time,
                            self.cur_time))
                        print("Queue size is{}".format(self.current_queue_size))
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

                if DEBUG:
                    print("packet {}: | arrival: {} | process: {} | departure: {} | cur: {}|".format(
                        self.current_packet.get_packetno(),
                        self.current_packet.get_arrivaltime(), self.cur_proc, self.cur_departure_time,
                        self.cur_time))
                    print("Queue size is{}".format(self.current_queue_size))

            # Current packet still processing
            else:
                server_queue.put(incoming)
                self.cur_time = inc_arrival_time
                self.output_arrival(incoming)
                print("Queue size is{}".format(self.current_queue_size))
                self.current_queue_size += 1
                self.total_cust += 1


    def get_process_time(self,incoming_pkt):
        # if DEBUG:
        #     print("size "+ str(incoming_pkt.get_packet_size()) + "| rate: " + str(self.RATE) )
        #     print(str(incoming_pkt.get_packet_size()/self.RATE))
        return incoming_pkt.get_packet_size()/self.RATE

    def output_arrival(self,incoming_pkt):
        global MAX_QUEUE_SIZE
        # [3749.00]: pkt 2748 arrives and finds 38 packets in the queue
        print("[{}] pkt {} arrives and finds {} in the queue").format(float(self.cur_time),
                                                              incoming_pkt.get_packetno(),
                                                              self.current_queue_size)

        # TODO: P[0..11] updating, if its over 10 in queue P[11] incremented [DONE]
        if P.get(self.current_queue_size) is None:
            P[self.current_queue_size] = 0
        P[self.current_queue_size] += 1

        if MAX_QUEUE_SIZE < self.current_queue_size:
            MAX_QUEUE_SIZE = self.current_queue_size

        # TODO update queue size total ie total_customers [DONE]
        # self.total_cust += (self.current_queue_size + 1)
        # print(self.total_cust)

    def output_departure(self,packet,sojourn):
        # [4638.00]: pkt 6102 departs having spent 243.00 us in the system
        print("[{}] pkt {} departs having spent {} us in the system".format(
            float(self.cur_time), packet.get_packetno(), sojourn
        ))

    def calculate_sojourn(self, current_packet, current_time):
        sojourn = current_time - current_packet.get_arrivaltime()
        self.total_sojourn += sojourn
        return sojourn

    def calculate_departure(self, packet, current_time):
        return (current_time + self.get_process_time(packet))

    def generateSource(self):
        source = SourceModel(self.N_PKTS,float(sys.argv[2]),PACKET_SIZE_MEAN)
        self.sourceModel = source
        self.source_queue = source.generate_packets()

    def get_sojourn(self):
        return self.total_sojourn

    def get_total_customers(self):
        return self.total_cust

    def read_from_file(self, FILENAME):
        self.sourceModel = SourceModel(0,0,0)
        self.source_queue = self.sourceModel.generate_from_file(FILENAME)

    def get_total_packets(self):
        return self.total_packets



def main():
    if len(sys.argv) == 2:
        FILENAME = sys.argv[1]
    # print(FILENAME)
        EventHandler = Event(0,0)
        EventHandler.read_from_file(FILENAME)
        EventHandler.start_sim()
        print_statistics(EventHandler.get_total_customers(),EventHandler.get_sojourn(), EventHandler.get_total_packets())

    elif len(sys.argv) < 3:
        print("Usage: {} npkts lambda".format(sys.argv[0]))

    else:
        # for x in range(len(sys.argv)):
        #     print(sys.argv[x])
        # #
        EventHandler = Event(int(sys.argv[1]),float(sys.argv[2]))
        # print(sys.argv[1])
        EventHandler.generateSource()
        EventHandler.start_sim()
        print_statistics(EventHandler.get_total_customers(),EventHandler.get_sojourn(),EventHandler.get_total_packets())
    plot_graph()


def print_statistics( total_customers ,total_sojourn_time, num_packets):
    avg_customer = float(float(total_sojourn_time)/num_packets)
    print("------------ STATISTICS ------------")
    print("N: {0:.2f} average number of packets in the system".format(float(float(total_customers)/num_packets)))
    print("T: {0:.2f} the average time spent by customer in the system".format(avg_customer))

    print("\nProbabilities")
    # for x in range(0,12):
    #     print("P[" + str(x) + "] = {}".format(float(P[x])/num_packets))

def plot_graph():

    # Find max queue size
    for x in range(0, MAX_QUEUE_SIZE+1):
        big_array.append(P[x])

    plt.plot(range(0,MAX_QUEUE_SIZE +1) , big_array)
    plt.show()



if __name__ == '__main__':
    main()
