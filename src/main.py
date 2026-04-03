import time
import meshtastic
import meshtastic.tcp_interface
import meshtastic.serial_interface
from pubsub import pub

class PortNums:
    UNKNOWN_APP = "UNKNOWN_APP"
    TEXT_MESSAGE_APP = "TEXT_MESSAGE_APP"
    REMOTE_HARDWARE_APP = "REMOTE_HARDWARE_APP"
    POSITION_APP = "POSITION_APP"
    NODEINFO_APP = "NODEINFO_APP"
    ROUTING_APP = "ROUTING_APP"
    ADMIN_APP = "ADMIN_APP"
    TEXT_MESSAGE_COMPRESSED_APP = "TEXT_MESSAGE_COMPRESSED_APP"
    WAYPOINT_APP = "WAYPOINT_APP"
    AUDIO_APP = "AUDIO_APP"
    DETECTION_SENSOR_APP = "DETECTION_SENSOR_APP"
    ALERT_APP = "ALERT_APP"
    KEY_VERIFICATION_APP = "KEY_VERIFICATION_APP"
    REPLY_APP = "REPLY_APP"
    IP_TUNNEL_APP = "IP_TUNNEL_APP"
    PAXCOUNTER_APP = "PAXCOUNTER_APP"
    STORE_FORWARD_PLUSPLUS_APP = "STORE_FORWARD_PLUSPLUS_APP"
    NODE_STATUS_APP = "NODE_STATUS_APP"
    SERIAL_APP = "SERIAL_APP"
    STORE_FORWARD_APP = "STORE_FORWARD_APP"
    RANGE_TEST_APP = "RANGE_TEST_APP"
    TELEMETRY_APP = "TELEMETRY_APP"
    ZPS_APP = "ZPS_APP"
    SIMULATOR_APP = "SIMULATOR_APP"
    TRACEROUTE_APP = "TRACEROUTE_APP"
    NEIGHBORINFO_APP = "NEIGHBORINFO_APP"
    ATAK_PLUGIN = "ATAK_PLUGIN"
    MAP_REPORT_APP = "MAP_REPORT_APP"
    POWERSTRESS_APP = "POWERSTRESS_APP"
    RETICULUM_TUNNEL_APP = "RETICULUM_TUNNEL_APP"
    CAYENNE_APP = "CAYENNE_APP"
    PRIVATE_APP = "PRIVATE_APP"
    ATAK_FORWARDER = "ATAK_FORWARDER"
    MAX = "MAX"
    

def onReceive(packet: dict, interface): # called when a packet arrives
    if "decoded" in packet:
        if packet["decoded"]["portnum"] == PortNums.TEXT_MESSAGE_APP and "text" in packet["decoded"]:
            print(f"From: {packet['from']}, To: {packet['to']}, message: {packet['decoded']['text']}")
        else:
            print(f"From: {packet['from']}, To: {packet['to']}, Port: {packet['decoded']['portnum']}")
    else:
        print(f"From: {packet['from']}, To: {packet['to']}")
        
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(str(packet)+"\n\n")

def onConnection(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # defaults to broadcast, specify a destination ID if you wish
    # interface.sendText("Ping")
    print("Connected to radio")

pub.subscribe(onReceive, "meshtastic.receive")
pub.subscribe(onConnection, "meshtastic.connection.established")
interface = meshtastic.serial_interface.SerialInterface()

while True:
    time.sleep(1000)
interface.close()