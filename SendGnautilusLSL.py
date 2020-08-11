import matplotlib.pyplot as plt
from pylsl import StreamInfo, StreamOutlet
from pygds import GDS
import re
import pygds


def configure_device(d, testsignal = False):
    #Amplifier settings
    d.Counter = 1
    d.BatteryLevel = 1
    d.NoiseReduction = 0
    d.CAR = 0
    d.ValidationIndicator = 0
    d.AccelerationData = 0
    d.LinkQualityInformation = 0

    #Configure Input source
    if testsignal:
        d.InputSignal = pygds.GNAUTILUS_INPUT_SIGNAL_TEST_SIGNAL
    else:
        d.InputSignal = pygds.GNAUTILUS_INPUT_SIGNAL_ELECTRODE

    #Configure Sample rate
    d.SamplingRate = 250
    #Configure Network Channel
    d.NetworkChannel =25
    # Configure Channels
    sensitivities = d.GetSupportedSensitivities()[0]
    for idx in range(32):
        ch = d.Channels[idx]
        ch.Acquire = 1
        ch.BipolarChannel = -1  # -1 => to GND
        ch.UsedForNoiseReduction = 0
        ch.UsedForCAR = 0
        #Set filters and sensitivity
        ch.NotchFilterIndex = 1 # 58hz-62Hz
        ch.BandpassFilterIndex = 13 #0.5Hz-30hz
        ch.Sensitivity = 750000.0
        # set configuration to device
    d.SetConfiguration()

def get_device_name(d):
    name = d.GetDeviceInformation()[0].split('\n')[1]
    name = re.findall('(?<=SERIAL_BS=).+',name)[0]
    return name

def print_device_configuration(d):
    pass

class DataSender:
    def __init__(self, oulet):
        self.outlet =oulet

    def send_data (self, data):
        print(data[0,:32].shape)

        self.outlet.push_sample(data[:,:32].reshape(-1))
        return True

def main():
    # Create Gnautilus device
    d = GDS()
    configure_device(d)
    device_name = get_device_name(d)

    # Create LSL outlet
    info = StreamInfo(device_name, 'eeg', 32, d.SamplingRate, 'float32', device_name)
    # Append channel meta-data
    info.desc().append_child_value("manufacturer", "G.tec")
    channels = info.desc().append_child("channels")
    for c in d.GetChannelNames()[0]:
        channels.append_child("channel") \
            .append_child_value("name", c) \
            .append_child_value("unit", "microvolts") \
            .append_child_value("type", "EEG")

    outlet = StreamOutlet(info)#, chunk_size=2)
    sender = DataSender(outlet)

    print(device_name)
    try:
        d.GetData(1, sender.send_data)
    finally:
        print("Closing device")
        d.Close()


if __name__ == '__main__':
    main()

