"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_stream
import cv2
import numpy as np
import time
import simpleaudio as sa

#Eye tracker window
cv2.namedWindow('EyeTrackerData', cv2.WINDOW_NORMAL)

frameBase = np.zeros((200,200,3))
frame     = np.zeros((200,200,3))
color = (255,0,0)
centerPoint = (100,100)
lastSampleTime = 0

#Alarm sound
alarm = sa.WaveObject.from_wave_file('./sounds/beep-07.wav')

# first resolve an EEG stream on the lab network
print("looking for an EEG stream...")
streams = resolve_stream('name', 'gaze_position')

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])

print("hello")
counter = 0
try:
    while True:

        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        try:
            sample, timestamp = inlet.pull_sample(0.055)
            centerPoint = (int(sample[2] * 199), int(sample[3] * 199))

            #If there is an error in the previous line I won't reach here
            # print(timestamp, sample)
            lastSampleTime =  time.time()

        except Exception as e:
            #print(e, ". Probably because of a timeout error :(")
            counter += 1
            print(counter, "Time since last sample", time.time() - lastSampleTime)

        #Update position of the cursor
        frame = frameBase.copy()
        frame = cv2.circle(frame, centerPoint, radius=8, thickness=-1,color=color)
        cv2.waitKey(1)
        cv2.imshow('EyeTrackerData', frame)

        if time.time() - lastSampleTime > 0.8:
            play_obj = alarm.play()
            play_obj.wait_done()
            time.sleep(0.5)
            lastSampleTime = time.time()


except Exception as e:
    print("Closing Script")
    print(e)

finally:
    cv2.destroyAllWindows()