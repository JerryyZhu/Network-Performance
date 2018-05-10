#!/usr/bin/python
# sudo mn --custom fat_topo.py --topo mytopo --arp --controller=remote,ip=127.0.0.1,port=55555
# sudo ryu-manager RyuController.py ryu.app.ofctl_rest --ofp-tcp-listen-port 55555 --verbose


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController

from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

offset = 1

def str2dpid(dpid_string):
    """Given 8 integers separated by ':', convert the string into an
    equivalent hexadecimal representation (also stored as a string)"""
    # e.g. "0:1:2:3:4:5:6:255", 8 integers
    # convert each component into hex, then concat together
    dpid_comp = dpid_string.split(":")
    for i in xrange(len(dpid_comp)):
        dpid_comp[i] = '%.2X' % int(dpid_comp[i])
    return ''.join(dpid_comp)

class FatTreeTopo(Topo):
    """Creates a Fat-Tree Topology, specified for k pods"""
    # 4-level topology, consisting of hosts / switches
    hostList = None     # stores node names in order (left to right)
    edgeList = None
    aggrList = None
    coreList = None

    def test(self):
        switch = self.addSwitch("crSW01", dpid = str2dpid("0:0:0:0:0:2:1:1"))
        print("Switch DPID:" + str2dpid("0:0:0:0:0:2:1:1"))
        print("expecting DPID of 131329")
        host = self.addHost("h01", ip = "10.1.1.1")
        host2 = self.addHost("h02", ip = "10.1.1.2")
        self.addLink(host, switch, port1=1, port2 = 1)
        self.addLink(host2, switch, port1=1, port2 = 2)


    # init
    def build(self, k=2):
      #  self.test()
       # return

        # Initialise the lists
        coreList = []
        aggrList = []
        edgeList = []
        hostList = []
        k = 4

        # Create core switches
        count = 1
        for j in range(1, (k/2 + 1)):
            for i in range(1, (k/2 +1)):
                core = self.addSwitch("crSW%02d" % (count), dpid = str2dpid("0:0:0:0:0:%d:%d:%d" % (k,j,i)))
                coreList.append(core)
                count +=1

        # Create pod switches, aggregation and edge switches
        # Create hosts and link each host to edges
        # Connect each aggregation to edge switch as well

        # Pod switch is
        hostCount = 0
        for pod in range(k): # pods are [0, k-1]
            countCore = 0
            for switch in range(k/2):
                # Edge switch is [0, k/2 -1]
                # Aggr switch is [k/2, k-1]
                aggr = self.addSwitch("agSw%02d%02d" % (pod, switch), dpid = str2dpid("0:0:0:0:0:%d:%d:%d" % (pod, switch + k/2, 1)))
                edge = self.addSwitch("edSw%02d%02d" % (pod, switch), dpid = str2dpid("0:0:0:0:0:%d:%d:%d" % (pod, switch, 1)))
                aggrList.append(aggr)
                edgeList.append(edge)

                # Link aggr to core router
                for i in range(k/2):
                    self.addLink(aggr, coreList[countCore], port1=(k/2 + i + offset), port2=pod + offset)
                    # print("Add link " + aggr + "eth" + str(k/2 + i) + "   " + coreList[countCore] + "eth" + str(pod))
                    countCore += 1

                # Create the hosts for new edge switch
                print("Assigning hosts for edge switch" + edge)
                for h in range(k/2):
                    host = self.addHost("h%d" % (hostCount), ip = "10.%d.%d.%d" % (pod,switch, h + 2))
                    self.addLink(host, edge, port1 = 1, port2 = h + offset)
                    # print("Host count: " + str(hostCount) + "port2: " + str(h))
                    hostList.append(host)
                    hostCount += 1

            # Link each edge switch to aggregation
            for e in range(k/2):
                current_edge = edgeList[pod*k/2 + e]
                # print("------- Assigning links for edge switch" + current_edge + "------------")
                for l in range(k/2):
                    # print(current_edge + "eth" + str(k/2 + l))

                    current_aggr = aggrList[pod*k/2 + l]
                    # print("Adding link to " + current_aggr + " eth" + str(e))

                    self.addLink(current_edge, current_aggr, port1 = (k/2 + l + offset), port2=e+offset)

        print(coreList)
        print(aggrList)
        print(edgeList)
        print(hostList)

def simpleTest():
    #"Create and test a simple network"
    topo = FatTreeTopo(k=2)
    net = Mininet( topo=topo, controller=lambda name: RemoteController( name, ip='0.0.0.0', port=8080 ) )
    # net = Mininet(topo=topo, controller=remote)
    # net = Mininet( topo=topo, controller=None)
    # net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6633 )
   # net = Mininet(topo=topo, controller=OVSController)
    net.start()
    #dumpNodeConnections(net.hosts)
    #dumpNodeConnections(net.switches)
    # net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()

topos = { 'mytopo': ( lambda: FatTreeTopo() ) }
