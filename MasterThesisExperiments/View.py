import cv2
from threading import Thread
import time
import numpy as np


'''
states
1 --> waiting user signal
2 --> doing the task
3 --> finish
'''

class View(Thread):

    def __init__(self, controller):
        super().__init__()
        self.red = (0, 0, 255)
        self.green = (0, 255, 0)
        self.controller = controller
        self.frame = self.init_view()
        self.wind_name = "Experiment timer"

    def init_view(self):

        img = np.zeros((1500, 2500, 3))
        totalDuration = 120

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, 'Recording user study', (10, 200), font, 5, (255, 255, 255), 5,
                    cv2.LINE_AA)
        cv2.putText(img, 'Press pedal to start'.format(totalDuration), (10, 400), font, 5, (255, 255, 255), 5,
                    cv2.LINE_AA)
        cv2.putText(img, 'Press pedal to end'.format(totalDuration), (10, 600), font, 5, (255, 255, 255), 5,
                    cv2.LINE_AA)

        img = self.update_view(img, "waiting", self.red, time = 0)
        return img

    def update_view(self, im, status, color, time):
        font = cv2.FONT_HERSHEY_SIMPLEX
        im[1100 - 200:, 10:, :] = 0
        im = cv2.putText(im, 'Status: {:}'.format(status), (10, 1100), font, 5, color, 5, cv2.LINE_AA)

        minutes = time // 60
        seconds = time % 60
        im = cv2.putText(im, 'time: {:02d}:{:02d}'.format(minutes, seconds), (10, 1300), font, 5, color, 5, cv2.LINE_AA)
        return im

    def run(self):
        try:
            cv2.namedWindow(self.wind_name, cv2.WINDOW_NORMAL)

            #Wait until user press the pedal
            while self.controller.task_state == "waiting user signal" and self.controller.running:
                # self.frame
                cv2.imshow(self.wind_name, self.frame)
                k = cv2.waitKey(30)

            #Count until the user finish the task
            while self.controller.task_state == "doing the task" and self.controller.running:
                new_time = self.controller.get_time()
                # print(new_time)
                self.frame = self.update_view(self.frame, self.controller.task_state, self.green, time = int(new_time))
                cv2.imshow(self.wind_name, self.frame)
                k = cv2.waitKey(30)

            self.frame = self.update_view(self.frame, self.controller.task_state, self.red, time=int(new_time))
            cv2.imshow(self.wind_name, self.frame)
            k = cv2.waitKey(0)

            self.controller.running = False

            print("Closing view")
        except KeyboardInterrupt:
            print("Keyboard interruption")

class DummyController:
    def __init__(self):
        self.running = True
        self.task_state = "waiting user signal"
        self.time = 0

    def get_time(self, ):
        return self.time

if __name__ == "__main__":
    dummy = DummyController()
    view = View(dummy)
    view.start()

    time.sleep(2)
    dummy.task_state = "doing the task"

    init_time = time.time()

    while time.time() - init_time<10:
        dummy.time = time.time() - init_time
        time.sleep(0.5)

    dummy.task_state = "finished"
    view.join()