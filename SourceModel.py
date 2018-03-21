# Poisson Source Model
# Queue space infinite
# The source generates packets as a Poisson process at a specified rate lambda.
# The following notation is used: us for microseconds, ms for milliseconds, and sec for seconds.


from EventPkt import *
import random
import math
import queue

class SourceModel:

    # Generate exponential sized packets
    packet_size_mean = 1250
    input_lambda = 0
    num_packets = 0

    def __init__(self,num_packets,input_lambda,packet_size_mean):
        self.packet_size_mean = packet_size_mean
        self.input_lambda = input_lambda
        self.num_packets = num_packets

    # Source:
    # https://stackoverflow.com/questions/2106503/pseudorandom-number-generator-exponential-distribution
    # Alternatively using random.expovariate which does the same thing

    def generate_packets(self):
        q = queue.Queue()
        time = 0
        max = self.num_packets + 1
        for x in range(1, max):
            # Generate an interval between packet arrival, ie time til next arrival
            interval = self.exponential_number_generator(self.input_lambda)
            time = time + interval

            # Create a new packet
            p = EventPkt(x, self.generate_size(), time)
            q.put(p)
        return q


    def generate_size(self):
        # return -1 * math.log(1.0 - random.random()) / self.packet_size_mean
        return random.expovariate(self.packet_size_mean)
        # return -math.log(1.0 - random.random()) / rateParameter

    def exponential_number_generator(self,lambd):
        return -math.log(1.0 - random.random()) / float(lambd)