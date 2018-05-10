from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
import array
from ryu.lib import dpid

k = 4
PORT_OFFSET = 1


def coreDownLink():
    ip_list = []
    output_list = []

    for count in range(k):
        ip = ('10.%d.0.0' % (count), '255.255.0.0')
        ip_list.append(ip)
        output_list.append(count + PORT_OFFSET)

    return ip_list, output_list

def upLink(pod,switch):
    ip_list = []
    output_list = []

    for count in range(2,int(k/2) + 2): #core and aggr switch has the same uplink info
        ip = ('0.0.0.%d'%(count),'0.0.0.255')
        ip_list.append(ip)
        outputPort = ((count - 2 + switch)%int(k/2)) + int(k/2)
        output_list.append(outputPort + PORT_OFFSET)

    return ip_list, output_list


def downLink(pod, switch):
    ip_list = []
    output_list = []

    for count in range(0, k / 2):  # calculates list of output
        output_list.append(count + PORT_OFFSET)

    if switch <= ((k / 2) - 1):  # if switch is edgeSwitch (needs last seg)
        for count in range(2, (k / 2 + 2)):
            ip = ('10.%d.%d.%d' % (pod, switch, count), '255.255.255.255')  # dest_ip to hosts, only last one changes
            ip_list.append(ip)

    # if switch > int(k / 2) - 1:  # if switch is aggrSwitch (doesnt need last seg)
    else:
        for count in range(k / 2):
            ip = ('10.%d.%d.0' % (pod, count), '255.255.255.0')
            ip_list.append(ip)

    return ip_list, output_list

# Inherits from ryu.base.app_manager
class TestSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TestSwitch, self).__init__(*args, **kwargs)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match = match, instructions = inst)
        datapath.send_msg(mod)

    # Hand shake handler? Called when switch first talks to controller
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        ip_list = []
        port_list = []

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        dpid_ = dpid.dpid_to_str(datapath.id)
        print("Switch found with dipid" + dpid_)
        print(datapath)

        # Add flow entries

        pod = int(dpid_[10:12])
        switch_num = int(dpid_[12:14])

        # Check if core switch
        if (pod == k):
            # Handle core switches
            # Push down links
            downLinkFlow, outputPort1 = coreDownLink()
        # Must be aggregation/edge switch
        else:
            downLinkFlow, outputPort1 = downLink(pod, switch_num)
            upLinkFlow, outputPort2 = upLink(pod, switch_num)

        for i in range(len(downLinkFlow)):
            match = parser.OFPMatch(ipv4_dst=downLinkFlow[i], eth_type=0x800)
            actions = [parser.OFPActionOutput(outputPort1[i],ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 10, match, actions)

        # Add suffix entries to table since Switch is not Core
        if switch_num != k:
            for i in range(len(upLinkFlow)):
                match = parser.OFPMatch(ipv4_dst=upLinkFlow[i], eth_type=0x800)
                actions = [parser.OFPActionOutput(outputPort2[i],ofproto.OFPCML_NO_BUFFER)]
                self.add_flow(datapath, 1, match, actions)

        # table miss entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions) \


        @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
        def packet_in_handler(self, ev):
            datapath = ev.msg.datapath
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            pkt = packet.Packet(array.array('B', ev.msg.data))

            switchDPID = datapath.id
            dpid_ = dpid.dpid_to_str(datapath.id)
            # print('{} is receiving packets' .format(dpid))

            # print(pkt)

