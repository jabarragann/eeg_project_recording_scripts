"""
Created on Thu Feb 21 16:20:32 2019
@author: Juan Antonio Barragán Noguera
@email: jabarragann@unal.edu.co
"""

# !/usr/bin/python
import sys, struct, serial, time
import matplotlib.pyplot as plt
from pylsl import StreamInfo, StreamOutlet

def wait_for_ack():
    ddata = b""
    ack = struct.pack('B', 0xff)
    while ddata != ack:
        ddata = ser.read(1)
        # print ( "0x%02x" % ddata[0] )

    return


def send_stop_streaming_command():
    ser.write(struct.pack('B', 0x20))
    print
    print("stop command sent, waiting for ACK_COMMAND")
    wait_for_ack()
    print("ACK_COMMAND received.")
    # close serial port
    ser.close()
    print("All done")


# Global Variables
start, end = [0, 0]
accumulate = 0
timestamp_arr = []
ppgArr = []
gsrArr = []
numb_seconds = 20
fileName = "./sensor_data99.csv"

if __name__ == '__main__':
    if len(sys.argv) < 2 and False:
        print("no device specified")
        print("You need to specify the serial port of the device you wish to connect to")
        print("example:")
        print("   aAccel5Hz.py Com12")
        print("or")
        print("   aAccel5Hz.py /dev/rfcomm0")
    else:

        # ser = serial.Serial(sys.argv[1], 115200)
        ser = serial.Serial('Com8', 115200)
        ser.flushInput()
        print("port opening, done.")

        # send the set sensors command
        ser.write(struct.pack('BBBB', 0x08, 0x04, 0x01, 0x00))  # GSR and PPG
        wait_for_ack()
        print("sensor setting, done.")

        # Enable the internal expansion board power
        ser.write(struct.pack('BB', 0x5E, 0x01))
        wait_for_ack()
        print("enable internal expansion board power, done.")

        # send the set sampling rate command

        '''
         sampling_freq = 32768 / clock_wait = X Hz
        '''
        sampling_freq = 204.80
        clock_wait = int((2 << 14) / sampling_freq)

        ser.write(struct.pack('<BH', 0x05, clock_wait))
        wait_for_ack()

        # send start streaming command
        ser.write(struct.pack('B', 0x07))
        wait_for_ack()
        print("start command sending, done.")

        # read incoming data
        ddata = b""
        numbytes = 0
        framesize = 8  # 1byte packet type + 3byte timestamp + 2 byte GSR + 2 byte PPG(Int A13)

        start = time.time()
        print("Packet Type\tTimestamp\tGSR\tPPG")

        #Create LSL outlet
        ppgInfo = StreamInfo('Shimmer_ppg', 'PPG', 1, sampling_freq, 'float32', 'ppgId1_mv')
        ppgOutlet = StreamOutlet(ppgInfo)
        gsrInfo = StreamInfo('Shimmer_gsr', 'GSR', 1, sampling_freq, 'float32', 'gsrId2_ohm')
        gsrOutlet = StreamOutlet(gsrInfo)

        print("Streaming data ...")
        try:
            # Take numb_seconds seconds of data
            while True:
                while numbytes < framesize:
                    ddata += ser.read(framesize)
                    numbytes = len(ddata)

                computer_time = time.time()
                end = time.time()
                accumulate += end - start
                freq = 1 / (end - start + 0.00000000000001)
                # print(freq, accumulate)
                start = time.time()

                start = time.time()
                data = ddata[0:framesize]
                ddata = ddata[framesize:]
                numbytes = len(ddata)

                # read basic packet information
                (packettype) = struct.unpack('B', data[0:1])
                (timestamp0, timestamp1, timestamp2) = struct.unpack('BBB', data[1:4])

                # read packet payload
                (PPG_raw, GSR_raw) = struct.unpack('HH', data[4:framesize])

                # get current GSR range resistor value
                Range = ((GSR_raw >> 14) & 0xff)  # upper two bits
                if (Range == 0):
                    # kohm
                    Rf = 40.2
                elif (Range == 1):
                    # kohm
                    Rf = 287.0
                elif (Range == 2):
                    # kohm
                    Rf = 1000.0
                elif (Range == 3):
                    # kohm
                    Rf = 3300.0
                else:
                    Rf = 0
                    print("error")

                # convert GSR to kohm value
                gsr_to_volts = (GSR_raw & 0x3fff) * (3.0 / 4095.0)
                GSR_ohm = Rf / ((gsr_to_volts / 0.5) - 1.0)

                # convert PPG to milliVolt value
                PPG_mv = PPG_raw * (3000.0 / 4095.0)

                timestamp = timestamp0 + timestamp1 * 256 + timestamp2 * 65536
                sensor_time = timestamp

                print("0x%02x\t\t%5d,\t%4d,\t%4d" % (packettype[0], timestamp, GSR_ohm, PPG_mv))

                ppgOutlet.push_sample([PPG_mv])
                gsrOutlet.push_sample([GSR_ohm])


        finally:
            # send stop streaming command
            print("closing procedure")
            send_stop_streaming_command()