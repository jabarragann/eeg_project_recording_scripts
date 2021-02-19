from OddBallTask.OddBallTask.MakeSounds_Oddball import *
import numpy as np
import time
import pygame
import signal
import sys

def signal_handler():
    print("Script ended by user")
    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':

    ITI = 600 # in ms
    nu_sounds = 3000
    duration = 100 # sound duration in ms
    nu_blocks = 2
    standard = 2000 # frequencies in Hz
    deviant = 440   # frequencies in Hz
    ratio_deviant = 0.2
    date = (time.strftime("%m%d%Y-%I%M%S"))
    p_id = 13

    #Create sequence and sounds
    deviant_sounds = create_sequence_of_deviant(3000,0.15,40)
    Sounds = create_sounds([standard, deviant],100)
    #init mixer
    pygame.mixer.pre_init(44100, -16, 2, p_id)  # setup mixer to avoid sound lag
    pygame.init()

    tr = 0
    last_time = time.time()
    S2pl = pygame.mixer.Sound(Sounds[0, :].astype('int16'))  # prepare first sound
    while tr < nu_sounds - 1:

        # prepare buffer for next trial:
        if time.time() - last_time > ITI / 1000 - 0.005:
            if tr+1 in deviant_sounds:
                # print("deviant")
                S2pl = pygame.mixer.Sound(Sounds[0, :].astype('int16'))
            else:
                S2pl = pygame.mixer.Sound(Sounds[1, :].astype('int16'))
            tr += 1

            if tr in deviant_sounds:
                #Send deviant event to lsl
                alarm_time = pygame.time.get_ticks()
                print(alarm_time)
            else:
                #Send normal event to lsl
                pass

            S2pl.play()
            last_time = time.time()
        else:
            time.sleep(0.001)

        signal.signal(signal.SIGINT, signal_handler)



    pygame.quit()



    # for i in range(20):
    #     S2pl = pygame.mixer.Sound(Sounds[i%3, :].astype('int16'))
    #     S2pl.play()
    #
    #     time.sleep(0.3)