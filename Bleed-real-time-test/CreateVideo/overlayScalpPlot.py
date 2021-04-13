import numpy as np
import cv2
import matplotlib.pyplot as plt
import pickle


#Load scalp plots
plotsDict = pickle.load(open("./../highTrial/scalp.pickle","rb")
                        )
plot = plotsDict['img']
ts = plotsDict['ts']

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture('video_left_color.avi')

# Check if camera opened successfully
if not cap.isOpened():
    print("Error opening video stream or file")

# Read until video is completed
counter = 0
scalpIdx = 0
while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()
    counter += 1
    if ret:

        if counter%30 == 0:
            scalpIdx += 1
        img = plot[scalpIdx]
        img = cv2.resize(img, dsize=(360, 90), interpolation=cv2.INTER_CUBIC)

        # gray = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        # ret, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        # img[thresh == 255] = 0

        imgForBlending = frame.copy()
        # imgForBlending[0:0 + img.shape[0], 50:50 + img.shape[1], :] = img

        h,w,d = frame.shape
        imgForBlending[0:0 + img.shape[0], w-img.shape[1]:w, :] =  \
            imgForBlending[0:0 + img.shape[0], w-img.shape[1]:w, :] * 0.2 + img * 0.8
        # imgForBlending[0:0 + img.shape[0], 50:50 + img.shape[1], :] =  imgForBlending[0:0 + img.shape[0], 50:50 + img.shape[1], :] * 0.5 + img * 0.5
        # display image with opencv or any operation you like
        cv2.imshow("plot1", img)
        cv2.imshow("plot2", imgForBlending)

        # Display the resulting frame
        # cv2.imshow('Frame',frame)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    # Break the loop
    else:
        break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
