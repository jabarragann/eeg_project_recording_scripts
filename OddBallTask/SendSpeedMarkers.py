"""Example program to demonstrate how to send string-valued markers into LSL."""

import random
import time

from pylsl import StreamInfo, StreamOutlet


def main():
    info = StreamInfo(name ='Oddball_speed', type='Markers', channel_count =1, nominal_srate=0,
                      channel_format='string', source_id='velocity')

    # next make an outlet
    outlet = StreamOutlet(info)

    while True:
        # pick a sample to send an wait for a bit
        speed = input("new speed? ")
        outlet.push_sample([speed])


if __name__ == '__main__':
    main()