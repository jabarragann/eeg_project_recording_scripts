from threading import Thread
import time
from OddBallTask.OddBallTask.MakeSounds_Oddball import *
import numpy as np
import time
import pygame
import signal
import sys
from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
from pylsl import  resolve_byprop

def create_lsl_stream(name=None, type=None, channel_count=None, nominal_srate=None,
                      channel_format=None, source_id=None):
    info = StreamInfo(name=name, type=type, channel_count=channel_count, nominal_srate=nominal_srate,
                      channel_format=channel_format, source_id=source_id)
    outlet = StreamOutlet(info)
    return outlet


class OddBallModule(Thread):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        #Config Variables
        self.ITI = 1000#500  # in ms
        self.nu_sounds = 4000
        self.duration = 100  # sound duration in ms
        self.nu_blocks = 2
        self.deviant = 440; self.standard = 2000 # frequencies in Hz
        self.ratio_deviant = 0.15
        self.p_id = None

        # Create sequence and sounds
        self.deviant_sounds = create_sequence_of_deviant(self.nu_sounds, self.ratio_deviant, self.p_id)
        self.Sounds = create_sounds([self.standard, self.deviant], self.duration)
        # init mixer
        pygame.mixer.pre_init(44100, -16, 2, 512)  # setup mixer to avoid sound lag
        pygame.init()
        #Running variables
        self.tr = 0

        #Create lsl output streams
        self.odd_alarm_outlet    = create_lsl_stream(name="odd_alarm",type="Markers",channel_count=1,nominal_srate=0,
                                                  channel_format="string",source_id="odd123124")


    def listen_speed_markers(self):
        count = 0
        while self.controller.running:
            streams = resolve_byprop('name', 'Oddball_speed', timeout=1)

            if len(streams) > 0 :
                inlet = StreamInlet(streams[0])
                print("oddball_speed stream found ")
                while self.controller.running:
                    sample, timestamp = inlet.pull_sample(timeout=1)
                    if timestamp is not None:
                        # print("got new speed %s at time %s" % (sample[0], timestamp))
                        self.ITI = int(sample[0])


                print('Close listening socket')
            else:
                print(count, "oddball_speed inlet not found")
                count += 1
    def run(self):
        while self.controller.running:
            # print("Secondary off")
            time.sleep(0.5)

            if self.controller.controller_secondary_on:
                last_time = time.time()
                S2pl = pygame.mixer.Sound(self.Sounds[0, :].astype('int16'))  # prepare first sound
                while self.tr < self.nu_sounds - 1 and self.controller.running and self.controller.controller_secondary_on:

                    # prepare buffer for next trial:
                    if time.time() - last_time > self.ITI / 1000 - 0.005:
                        if self.tr + 1 in self.deviant_sounds:
                            S2pl = pygame.mixer.Sound(self.Sounds[0, :].astype('int16')) #Deviant
                        else:
                            S2pl = pygame.mixer.Sound(self.Sounds[1, :].astype('int16'))
                        self.tr += 1

                        if self.tr in self.deviant_sounds:
                            # Send deviant event to lsl
                            alarm_time = pygame.time.get_ticks()
                            self.odd_alarm_outlet.push_sample(["odd_alarm"])
                            print(alarm_time)
                        else:
                            self.odd_alarm_outlet.push_sample(["normal_alarm"])

                        S2pl.play()
                        last_time = time.time()
                    else:
                        time.sleep(0.001)

                    # signal.signal(signal.SIGINT, self.signal_handler)

        pygame.quit()
        print("Finish oddball")