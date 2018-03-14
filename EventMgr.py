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


# Determine average number of customers in the system
# Determine average time each customer spent in the queue
# For each n between 0 and 10, the probability P(n) that an arriving packet finds n packets already in the system.


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

        # While both the source queue and server queue is not empty
        while ((source_queue.empty() == False) or (server_queue.empty() == False)):
            # Grab a packet from source queue
            if (source_queue.empty() == False):

                incoming = source_queue.get()

                # Case 1: Server queue empty
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

                    # Another packet is being processed
                    else:
                        inc_arrival_time = incoming.get_arrivaltime()
                        if (inc_arrival_time < current_end_time):
                            # Add to queue, don't do much
                            server_queue.put(incoming)
                            current_time = inc_arrival_time
                        else:
                            # Don't add to queue size counter since queue is empty
                            current_time = current_end_time # this may be wrong, do keep going through
                            current_packet = incoming
                            process_time = current_packet.get_packet_size()
                            new_end_time = inc_arrival_time + process_time
                            current_end_time = new_end_time


                # Case 2: Server queue is not empty
                else:
                    # Keep going through the queue to see if next packet end time earlier than
                    # current arrival time

                    # Compare incoming with what is in current
                    inc_arrival_time = incoming.get_arrivaltime()

                    while (server_queue.empty() == False):
                        if (current_end_time < inc_arrival_time):
                            # Current packet leaves, check to see if there are more packets in server
                            # queue and if they are earlier

                            # Todo stuff related to when packet leaves queue
                            current_time = current_end_time
                            current_packet = server_queue.get()
                            current_packet.set_start_time(current_time)

                        else:
                            # add the packet to the queue, since
                            server_queue.put(incoming)
                            current_time = inc_arrival_time
                            break


    def __init__(self, numPackets,packet_size_mean):
        self.numPackets = numPackets
        self.packet_size_mean = packet_size_mean

    def createSource(self):
        link_speed = 10 * 1000 * 1000 * 1000  # 10 Gbps connection