import pickle
import cv2
import numpy as np
import os.path
from pathlib import Path
import pandas as pd
path = './../LowTrial/'

# Create a VideoCapture object
video = cv2.VideoCapture(os.path.join(path,'video_left_color.avi'))
#Load selected frames
selectedFrames = pd.read_csv(os.path.join(path,'selectedVideoFrames.txt'))
selectedFrames.iloc[:,0] = selectedFrames.iloc[:,0] - selectedFrames.iloc[0,0]
firstFrame = int(selectedFrames.iloc[0,1])
#Read scalp plots
plotsDict = pickle.load(open(path + "/scalp.pickle","rb"))
plot = plotsDict['img']
ts = (plotsDict['ts'] - 250) / 250

#Read prediction plots
predictionPlots = pickle.load(open(path+"/predictionsImg.pickle","rb"))
predictionPlots = predictionPlots['img']

#Move video to starting frame
totalFrames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
video.set(1, firstFrame -1)

#Output Resolution
frame_width = int(video.get(3))
frame_height = int(video.get(4))
# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
out = cv2.VideoWriter(os.path.join(path,'finalVideo.avi'), cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))

counter = -1
scalpIdx = 0
scalp = plot[0]

while True:
    ret, frame = video.read()
    counter += 1
    if ret:
        if scalpIdx+1 < ts.shape[0]:
            if selectedFrames.iloc[counter,0] > ts[scalpIdx+1]:
                scalpIdx += 1
                print("current time, new scalp time", selectedFrames.iloc[counter,0], ts[scalpIdx])
        else:
            break

        img = plot[scalpIdx]
        img = cv2.resize(img, dsize=(360, 90), interpolation=cv2.INTER_CUBIC)
        h, w, d = frame.shape
        frame[0:0 + img.shape[0], w - img.shape[1]:w, :] = \
            frame[0:0 + img.shape[0], w - img.shape[1]:w, :] * 0.2 + img * 0.8

        bar = predictionPlots[scalpIdx]
        rate = 0.8
        bar = cv2.resize(bar, dsize=(int(150*rate),int(200*rate)), interpolation=cv2.INTER_CUBIC)

        frame[90:90 + bar.shape[0], w - bar.shape[1]:w, :] = \
            frame[90:90 + bar.shape[0], w - bar.shape[1]:w, :] * 0.2 + bar * 0.8

        # Write the frame into the file 'output.avi'
        out.write(frame)

        # Display the resulting frame
        cv2.imshow('frame', frame)

        # Press Q on keyboard to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Break the loop
    else:
        break

    # When everything done, release the video capture and video write objects
video.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()