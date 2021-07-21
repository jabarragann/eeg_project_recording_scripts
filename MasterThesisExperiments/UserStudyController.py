
import sys
sys.path.append("./../")
from MasterThesisExperiments.Timer import TimerModule
from MasterThesisExperiments.View import View
from MasterThesisExperiments.opts import  obtain_command_args
from threading import Thread
import threading

class Controller:
    def __init__(self):
        self.args = obtain_command_args()

        self.running = True

        self.timer_module = TimerModule(self)
        self.mouse_listener = threading.Thread(target=self.timer_module.listen_mouse_events)
        self.cognitive_predictions_listener = threading.Thread(target=self.timer_module.listen_for_cognitive_predictions)
        self.view_module = View(self)


        self.task_state = "waiting user signal"
        self.time = 0

    def get_time(self, ):
        return self.time

    def start(self):
        self.view_module.start()
        self.mouse_listener.start()
        if self.args.autonomy:
            self.cognitive_predictions_listener.start()
        self.timer_module.start()

        self.view_module.join()

if __name__ == "__main__":
    controller = Controller()
    controller.start()

