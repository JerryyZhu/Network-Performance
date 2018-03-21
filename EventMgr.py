# TELE4642 Network Performance: Lab 1

# Provides library functions to store events in order of their occurrence time.
# You need functions to efficiently add a new event, delete an existing event,
# and retrieve the next event. You may use a simple linked list to begin with.
# Think carefully about the types of events that can happen in your system
# (source state change, packet arrival/departure, ...)

import math
import random
import SourceModel
import Queue
import EventPkt
import sys


#sim npkts lambda lambda arrival rate

# Determine average number of customers in the system
# Determine average time each customer spent in the queue
# For each n between 0 and 10, the probability P(n) that an arriving packet finds n packets already in the system.

filename = "output.txt"

class EventMgr:

    numPackets = 0
    input_lambda = 1
    packet_size_mean = 0
    rate = 10000000000
    rate_us = rate/1000000
    queue_total

    def start_sim(self):
        incoming = None
        current_time = 0
        current_end_time = 0
        source = SourceModel.SourceModel(self.numPackets, self.input_lambda, self.packet_size_mean)
        current_packet = None

        # Get source model queue
        source_queue = source.generate_packets()

        # Create a server queue
        server_queue = Queue.Queue()

        # Create a output log file
        # [4638.00]: pkt 6102 departs having spent 243.00 us in the system

        # While both the source queue and server queue is not empty
        while ((source_queue.empty() == False) and (server_queue.empty() == False)):

            # Base case

            # Case 1: Server queue is not empty
            # Keep going through the queue to see if next packet end time earlier than
            # current arrival time

            # Compare incoming with what is in current
            inc_arrival_time = incoming.get_arrivaltime()

            while (server_queue.empty() == False):
                if (inc_arrival_time > current_end_time):
                    # Current packet leaves, check to see if there are more packets in server
                    # queue and if they are earlier

                    # Todo stuff related to when packet leaves queue
                    current_time = current_end_time
                    self.departure_message(current_packet, file, current_time)

                    # Get next packet from the queue

                    current_packet = server_queue.get()
                    current_packet.set_start_time(current_time)

                    # Find processing time
                    size = current_packet.get_packet_size()
                    process_time = size / self.rate_us
                    current_end_time = current_time + process_time

                else:
                    # add the packet to the queue, since
                    server_queue.put(incoming)
                    current_time = inc_arrival_time
                    break

            # Grab a packet from source queue
            incoming = source_queue.get()

            # Case 2: Server queue empty
            # get process time/ end time/ set current parameters
            if server_queue.empty():
                # Check to see if packet is currently being processed
                # Server queue empty, server not busy
                if current_packet == None:
                    current_packet = incoming
                    current_time = incoming.get_arrivaltime()
                    size = current_packet.get_packet_size()
                    process_time = size/self.rate_us
                    current_end_time = current_time + process_time
                    current_packet.set_endtime(current_end_time)
                    current_packet.set_processtime(process_time)
                    self.arrival_message(incoming, file)

                # Another packet is being processed
                else:
                    inc_arrival_time = incoming.get_arrivaltime()
                    # Packet arrives earlier before previous packet is processed
                    if (inc_arrival_time < current_end_time):
                        # Add to queue, don't do much
                        server_queue.put(incoming)
                        current_time = inc_arrival_time
                        self.arrival_message(incoming, file)
                    else:
                        # Previous packet has been processed
                        # Todo: Queue counter
                        current_time = current_end_time # this may be wrong, do keep going through
                        self.departure_message(current_packet, file, current_end_time)

                        # Arriving packet is now current packet
                        # Change current parameters
                        current_packet = incoming
                        process_time = current_packet.get_packet_size()/self.rate_us
                        new_end_time = inc_arrival_time + process_time
                        current_end_time = new_end_time



    def __init__(self, numPackets,packet_size_mean):
        self.numPackets = numPackets
        self.packet_size_mean = packet_size_mean

    def createSource(self):
        link_speed = 10 * 1000 * 1000 * 1000  # 10 Gbps connection

    def departure_message(self,packet,file, current_time):
        string =
        file.write()
        # [4638.00]: pkt 6102 departs having spent 243.00 us in the system

    def arrival_message(self, packet, file):
        string = '[' + packet.get_arrivaltime + ']'
        string += ' pkt ' + packet.getpacketno +

if __name__ == '__main__':
