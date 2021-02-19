from threading import Thread
import time
from OddBallTask.OddBallTask.MakeSounds_Oddball import *
import numpy as np
import time
import pygame
import signal
import sys
from pylsl import StreamInlet, resolve_stream

class OddBallModule(Thread):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        #Config Variables
        self.ITI = 600  # in ms
        self.nu_sounds = 3000
        self.duration = 100  # sound duration in ms
        self.nu_blocks = 2
        self.deviant = 440; self.standard = 2000 # frequencies in Hz
        self.ratio_deviant = 0.10
        self.p_id = 13

        # Create sequence and sounds
        self.deviant_sounds = create_sequence_of_deviant(self.nu_sounds, self.ratio_deviant, self.p_id)
        self.Sounds = create_sounds([self.standard, self.deviant], self.duration)
        # init mixer
        pygame.mixer.pre_init(44100, -16, 2, self.p_id)  # setup mixer to avoid sound lag
        pygame.init()
        #Running variables
        self.tr = 0

    # def run(self):
    #     count = 0
    #     while self.controller.running:
    #         print("Counting")
    #         print(count)
    #         count += 1
    #         time.sleep(2)

    def listen_speed_markers(self):
        streams = resolve_stream('name', 'Oddball_speed')
        inlet = StreamInlet(streams[0])

        print("oddball_speed stream found ")
        while self.controller.running:
            sample, timestamp = inlet.pull_sample(timeout=1)
            if timestamp is not None:
                self.ITI = int(sample[0])
                # print("got new speed %s at time %s" % (sample[0], timestamp))

        print('Close listening socket')

    def run(self):
        last_time = time.time()
        S2pl = pygame.mixer.Sound(self.Sounds[0, :].astype('int16'))  # prepare first sound
        while self.tr < self.nu_sounds - 1 and self.controller.running:

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
                    print(alarm_time)
                else:
                    # Send normal event to lsl
                    pass

                S2pl.play()
                last_time = time.time()
            else:
                time.sleep(0.001)

            # signal.signal(signal.SIGINT, self.signal_handler)

        pygame.quit()