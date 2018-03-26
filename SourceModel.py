# Poisson Source Model
# Queue space infinite
# The source generates packets as a Poisson process at a specified rate lambda.
# The following notation is used: us for microseconds, ms for milliseconds, and sec for seconds.


from EventPkt import *
import random
import math
import Queue

TEST = True

FILENAME = 'small_trace.txt'
class SourceModel:

    # Generate exponential sized packets
    packet_size_mean = 1250
    input_lambda = 0
    num_packets = 0
    server_queue = 0

    def __init__(self,num_packets,input_lambda,packet_size_mean):
        self.packet_size_mean = packet_size_mean
        self.input_lambda = input_lambda
        self.num_packets = num_packets

    # Source:
    # https://stackoverflow.com/questions/2106503/pseudorandom-number-generator-exponential-distribution
    # Alternatively using random.expovariate which does the same thing

    def generate_packets(self):
        q = Queue.Queue()
        time = 0.0
        max = self.num_packets + 1
        for x in range(1, max):
            # Generate an interval between packet arrival, ie time til next arrival
            interval = self.exponential_number_generator(self.input_lambda)
            # print(interval)
            time = time + interval
            # print(time)

            # Create a new packet
            p = EventPkt(x, self.generate_size(), float(time))
            # print("Packet {} made, size {}, arrival time {}".format(p.get_packetno(),p.get_packet_size(),
            #                                                         float(p.get_arrivaltime())))
            q.put(p)
        self.server_queue = q

        return q

    def generate_from_file(self, FILENAME):
        q = Queue.Queue()
        time = 0.0
        i = 1
        with open(FILENAME) as f:
            for line in f:

                # print (line)
                data = line.split()
                time = time + float(data[0])
                p = EventPkt(i,int(data[1]),time)
                if TEST:
                    print("Packet {} size {} arrival {}".format(i,int(data[1]),time))
                q.put(p)
                i = i + 1
        self.server_queue = q
        # if DEBUG:
        print("There are {} packets".format(i))
        self.num_packets = i
        return q

    def generate_size(self):
        # return -1 * math.log(1.0 - random.random()) / self.packet_size_mean
        size = random.expovariate(1.0/self.packet_size_mean)
        # print("Packet size = " + str(size))
        return size
        # return -math.log(1.0 - random.random()) / rateParameter

    def exponential_number_generator(self,lambd):
        # return -math.log(1.0 - random.random()) / float(lambd)
        return random.expovariate(lambd)

    def generate_packet(self):
        return self.server_queue.get()

    def get_num_packets(self):
        return self.num_packets

# Test code
def main():
    sourced = SourceModel(100,100,1250)
    # sourced.generate_packets()
    sourced.generate_from_file(FILENAME)
    print(sourced)

if __name__ == "__main__":
    main()
