from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
import array

# Inherits from ryu.base.app_manager
class TestSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TestSwitch, self).__init__(*args, **kwargs)

        # Initialise mac address tables

    # Hand shake handler?
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        print("Switch found with dipid" + str(datapath.id))
        print(datapath)

        # Table Miss Entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        # host = self.addHost("h01", ip = "10.1.1.1")
        # host2 = self.addHost("h02", ip = "10.1.1.2")

        # Add flows to two switches
        match = parser.OFPMatch(ipv4_dst = "10.1.1.1",eth_type = 0x800)
        actions = [parser.OFPActionOutput(1,ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath,1,match,actions)
        print("Flow added for 10.1.1.1")

        match = parser.OFPMatch(ipv4_dst = "10.1.1.2",eth_type = 0x800)
        actions = [parser.OFPActionOutput(2,ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath,1,match,actions)
        print("Flow added for 10.1.1.2")


    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match = match, instructions = inst)
        datapath.send_msg(mod)

#  https://github.com/osrg/ryu/blob/master/doc/source/library_packet.rst
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self,ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt = packet.Packet(array.array('B',ev.msg.data))
        for p in pkt.protocols:
            print p


        switchDPID = datapath.id
        dpid = format(switchDPID,'02x')
        dpid = str(dpid)
        zeros = 6 - len(dpid)
        #adds zeroes in front
        for i in range(zeros):
            strZero = '0'
            dpid = strZero + dpid
        print('{} is receiving packets' .format(dpid))
