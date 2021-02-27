
import sys
sys.path.append("./../")
from MasterThesisExperiments.Timer import TimerModule
from MasterThesisExperiments.View import View
from threading import Thread
import threading
class Controller():
    def __init__(self):
        self.timer_module = TimerModule(self)
        self.listener = threading.Thread(target=self.timer_module.listen_mouse_events)
        self.view_module = View(self)

        self.running = True
        self.task_state = "waiting user signal"
        self.time = 0

    def get_time(self, ):
        return self.time

    def start(self):
        self.view_module.start()
        self.listener.start()
        self.timer_module.start()

        self.view_module.join()

if __name__ == "__main__":
    controller = Controller()
    controller.start()

