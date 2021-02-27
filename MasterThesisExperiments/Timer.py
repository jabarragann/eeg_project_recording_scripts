from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
from pylsl import  resolve_byprop
from threading import Thread
import threading
import time
import simpleaudio as sa

def create_lsl_stream(name=None, type=None, channel_count=None, nominal_srate=None,
                      channel_format=None, source_id=None):
    info = StreamInfo(name=name, type=type, channel_count=channel_count, nominal_srate=nominal_srate,
                      channel_format=channel_format, source_id=source_id)
    outlet = StreamOutlet(info)
    return outlet

class TimerModule(Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.counting = False
        self.init_time = 0
        self.current_time = 0

        self.outlet = create_lsl_stream('ExperimentMarkers', 'Markers', 2, 0, 'string', 'myuidw43536')
        self.start_sound = sa.WaveObject.from_wave_file('./../sounds/beep-07.wav')
        self.end_sound = sa.WaveObject.from_wave_file('./../sounds/beep-10.wav')

        self.last_pressed = 0

    def run(self):
        while not self.counting and self.controller.running:
            time.sleep(0.5)

        self.start_signal()
        self.init_time = time.time()
        self.controller.task_state = "doing the task"
        while self.counting and self.controller.running:
            self.current_time = time.time() - self.init_time
            time.sleep(0.5)
            self.controller.time = self.current_time
            # print(self.current_time)

        self.end_signal()
        self.controller.task_state = "finished"

    def start_signal(self):
        for _ in range(3):
            play_obj = self.start_sound.play()
            play_obj.wait_done()
            time.sleep(1)
    def end_signal(self):
        play_obj = self.end_sound.play()
        play_obj.wait_done()

    def listen_mouse_events(self):
        count = 0
        while self.controller.running:
            streams = resolve_byprop('name', 'MouseButtons', timeout=1)

            if len(streams) > 0:
                inlet = StreamInlet(streams[0])
                print("oddball_speed stream found ")
                while self.controller.running:
                    sample, timestamp = inlet.pull_sample(timeout=1)
                    if timestamp is not None and sample[0] == "MouseButtonX2 pressed":
                        if time.time() - self.last_pressed > 3 :
                            self.last_pressed = time.time()
                            self.counting = not self.counting
                            print("got new speed %s at time %s" % (sample[0], timestamp))

                print('Close listening socket')
            else:
                print(count, "oddball_speed inlet not found")
            count += 1

class DummyController:
    def __init__(self):
        self.running = True
        self.task_state = "waiting user signal"
        self.time = 0

    def get_time(self, ):
        return self.time

if __name__ == "__main__":
    dummy = DummyController()
    timer_module = TimerModule(dummy)
    listener = threading.Thread(target=timer_module.listen_mouse_events, daemon=True)
    listener.start()
    timer_module.start()
    timer_module.join()
    print("finished")
