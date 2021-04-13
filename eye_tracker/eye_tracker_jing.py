# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 20:08:10 2020

@author: jy
"""
import time
import socket
import threading
import signal
import sys
#import pygst
import winsound
#pygst.require('0.10')
#import gst
import ast
timeout = 1.0
running = True


# GLASSES_IP = "fd93:27e0:59ca:16:76fe:48ff:fe05:1d43" # IPv6 address scope global
#GLASSES_IP = "10.46.16.86"
GLASSES_IP= "192.168.71.50" # IPv4 address 192.168.71.50"
PORT = 49152
#PORT=13006



# Keep-alive message content used to request live data and live video streams
KA_DATA_MSG = b"{\"type\": \"live.data.unicast\", \"key\": \"AHKQ0-V0R00-W1XYZ-G8J1N-121QP-XS53ZEK88\", \"op\": \"start\"}"
KA_VIDEO_MSG = b"{\"type\": \"live.video.unicast\", \"key\": \"AHKQ0-V0R00-W1XYZ-G8J1N-121QP-XS53ZEK88\", \"op\": \"start\"}"


# Gstreamer pipeline definition used to decode and display the live video stream
PIPELINE_DEF = "udpsrc do-timestamp=true name=src blocksize=1316 closefd=false buffer-size=5600 !" \
                "mpegtsdemux !" \
                "queue !" \
                "ffdec_h264 max-threads=0 !" \
                "ffmpegcolorspace !" \
                "xvimagesink name=video"


# Create UDP socket
def mksock(peer):
    iptype = socket.AF_INET
    if ':' in peer[0]:
        iptype = socket.AF_INET6
    return socket.socket(iptype, socket.SOCK_DGRAM)


# Callback function
def send_keepalive_msg(socket, msg, peser):
    while running:
        # print("Sending " + msg + " to target " + peer[0] + " socket no: " + str(socket.fileno()) + "\n")
        print("Sending " + str(msg) + " to target " + str(peer[0]) + " socket no: " + str(socket.fileno()) + "\n")
        socket.sendto(msg, peer)
        time.sleep(timeout)


def signal_handler(signal, frame):
    stop_sending_msg()
    sys.exit(0)


def stop_sending_msg():
    global running
    running = False


#if __name__ == "__main__":
signal.signal(signal.SIGINT, signal_handler)
peer = (GLASSES_IP, PORT)

# Create socket which will send a keep alive message for the live data stream
data_socket = mksock(peer)
#data_receive = mksock(peer)
td = threading.Timer(0, send_keepalive_msg, [data_socket, KA_DATA_MSG, peer])
td.start()
blink=0
z=[]
while running:
    # data, address = data_socket.recvfrom(100)
    data = data_socket.recv(100)
    data=ast.literal_eval(data.decode("utf-8"))
    z.append(data)
    try:

        if data['eye'] == 'right' and data['pd'] ==0 :
            #winsound.Beep(frequency=1200, duration=1000)
            #print('beep')
            blink = blink +1
            if blink > 6 :
                print('beep')
                winsound.Beep(frequency=1200, duration=1000)
                blink = 0

    except KeyError:
        pass