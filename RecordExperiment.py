import random
import time
import simpleaudio as sa
from pylsl import StreamInfo, StreamOutlet
import time
import numpy as np
import cv2
import sys

def changeState(im, status, color, time):
    im[1100-200:,10:,:] = 0
    im = cv2.putText(im, 'Status: {:}'.format(status), (10, 1100), font, 5, color, 5, cv2.LINE_AA)

    minutes = time // 60
    seconds = time % 60
    im = cv2.putText(im, 'time: {:02d}:{:02d}'.format(minutes,seconds), (10, 1300), font, 5, color, 5, cv2.LINE_AA)
    return im

#Get cli arguments
print(sys.argv)
if len(sys.argv)>=2:
	totalDuration = int(sys.argv[1])
else:
	print("Experiment default duration")
	totalDuration = 60*5

#Create marker stream
print("Creating marker stream ...\n")
info = StreamInfo('ExperimentMarkers', 'Markers', 2, 0, 'string', 'myuidw43536')
outlet = StreamOutlet(info)

#Load sound files
startSound = sa.WaveObject.from_wave_file('./sounds/beep-07.wav')
endSound = sa.WaveObject.from_wave_file('./sounds/beep-10.wav')
state = "Stop"
red   = (0,0,255)
green = (0,255,0)

print("Before starting the experiment make sure that:")
print("\t1) The G.Nautilus device is streaming data into LSL")
print("\t2) LabRecoder program is recording the data")
# input("Press any key to begin the experiment ")

img = np.zeros((1500,2500,3))

font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(img, 'Recording for {:d}s'.format(totalDuration), (10,200), font, 5, (255, 255, 255), 5, cv2.LINE_AA)
cv2.putText(img, 'Press s to start counting'.format(totalDuration), (10,400), font, 5, (255, 255, 255), 5, cv2.LINE_AA)
cv2.putText(img, 'Press q to stop and restart'.format(totalDuration), (10,600), font, 5, (255, 255, 255), 5, cv2.LINE_AA)
cv2.putText(img, 'Press ESC to exit'.format(totalDuration), (10,800), font, 5, (255, 255, 255), 5, cv2.LINE_AA)
# cv2.putText(img, 'Status: {:}'.format(state), (10,1100), font, 5, red, 5, cv2.LINE_AA)
img = changeState(img,"stop",red,0)

cv2.namedWindow('Experiment timer', cv2.WINDOW_NORMAL)
cv2.imshow('Experiment timer',img)

while True:
    k = cv2.waitKey(0)
    if k == 27:         # wait for ESC key to exit
        print("Exit program")
        cv2.destroyAllWindows()
        break
    elif k == ord('s'): # wait for 's' key to save and exit
        #Count time
        for _ in range(3):
            play_obj = startSound.play()
            play_obj.wait_done()
            time.sleep(1)

        startTime = time.time()
        outlet.push_sample(["started", "{:0.3f}".format(time.time())])

        img =changeState(img, "counting", green,0)
        cv2.imshow('Experiment timer', img)

        startTime = time.time()
        tempBeeps = 0
        prevTime = time.time()
        while  time.time()-startTime < totalDuration:
            if tempBeeps > 60:
                print("Experiment time ",time.time()-startTime)
                tempBeeps = 0
                play_obj = startSound.play()
                play_obj.wait_done()

            k2 = cv2.waitKey(1)
            if k2 == ord('q'):
                img = changeState(img, "stop", red, int(time.time()-startTime))
                cv2.imshow('Experiment timer', img)
                break
            else:
                img = changeState(img, "counting", green, int(time.time() - startTime))
                cv2.imshow('Experiment timer', img)

        outlet.push_sample(["ended", "{:0.3f}".format(time.time())])
        play_obj = endSound.play()
        play_obj.wait_done()
        img = changeState(img, "stop", red, int(time.time() - startTime))
        cv2.imshow('Experiment timer', img)


