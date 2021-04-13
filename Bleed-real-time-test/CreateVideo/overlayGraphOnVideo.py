import numpy as np
import cv2
import matplotlib.pyplot as plt

#Init graph
fig, ax = plt.subplots(1,1)
fig.patch.set_facecolor('grey')
fig.patch.set_alpha(0.4)
ax.set_facecolor((1.0, 0.47, 0.42))
fig.tight_layout()

x1 = np.linspace(0.0, 5.0)
x2 = np.linspace(0.0, 2.0)

y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
y2 = np.cos(2 * np.pi * x2)
line1, = ax.plot(x1, y1, 'ko-')        # so that we can update data later

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture('video_left_color.avi')

# Check if camera opened successfully
if not cap.isOpened():
    print("Error opening video stream or file")

# Read until video is completed
counter = 0
while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()
    counter += 1
    if ret:
        # update data
        line1.set_ydata(np.cos(2 * np.pi * (x1 + counter * 3.14 / 2)) * np.exp(-x1))
        fig.canvas.draw() # redraw the canvas

        # convert canvas to image
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        # img is rgb, convert to opencv's default bgr
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        img = cv2.resize(img, dsize=(48*3, 64*3), interpolation=cv2.INTER_CUBIC)

        imgForBlending = frame.copy()
        # imgForBlending[0:0 + img.shape[0], 50:50 + img.shape[1], :] = img

        h,w,d = frame.shape
        imgForBlending[0:0 + img.shape[0], w-img.shape[1]:w, :] =  \
            imgForBlending[0:0 + img.shape[0], w-img.shape[1]:w, :] * 0.5 + img * 0.5
        # imgForBlending[0:0 + img.shape[0], 50:50 + img.shape[1], :] =  imgForBlending[0:0 + img.shape[0], 50:50 + img.shape[1], :] * 0.5 + img * 0.5
        # display image with opencv or any operation you like
        cv2.imshow("plot1", img)
        cv2.imshow("plot2", imgForBlending)

        # Display the resulting frame
        cv2.imshow('Frame',frame)

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
