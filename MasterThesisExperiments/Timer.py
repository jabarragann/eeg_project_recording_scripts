from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
from pylsl import  resolve_byprop
from threading import Thread
import threading
import time
import simpleaudio as sa
import serial
import traceback
import socket

def create_lsl_stream(name=None, type=None, channel_count=None, nominal_srate=None,
                      channel_format=None, source_id=None):
    info = StreamInfo(name=name, type=type, channel_count=channel_count, nominal_srate=nominal_srate,
                      channel_format=channel_format, source_id=source_id)
    outlet = StreamOutlet(info)
    return outlet

class TimerModule(Thread):
    """
        The timer modules contains methods for the different stages of the experiment
    """

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

        if not self.controller.args.debug:
            # Create arduino serial port
            try:
                self.serial_connection = serial.Serial(port=self.controller.args.arduino_port, baudrate=9600, timeout=.2)
                time.sleep(1)
                print("Succesfully connected to arduino")
            except Exception as e:
                print("Check serial connection with arduino")
                self.controller.running = False
                exit(0)
            # Socket connection with DV computer
            try:
                self.server_socket, self.socket_connection = self.start_socket()
                print("Successfully connected to socket")
            except Exception as e:
                print("Check socket connection with DV computer. Client needs to be running beforehand")
                traceback.print_exc()
                self.controller.running = False
                exit(0)
        else:
            self.serial_connection = None
            self.socket_connection = None
            self.server_socket = None


    def start_socket(self):
        server_socket = socket.socket()  # get instance
        server_socket.settimeout(4)
        server_socket.bind((self.controller.args.server_address, self.controller.args.server_port))
        server_socket.listen(2)
        socket_connection, address = server_socket.accept()
        socket_connection.settimeout(4)
        print("Connection from: " + str(address))
        return server_socket, socket_connection

    def socket_command(self, cmd):
        list_of_cmds = ["turn on autonomy", "turn off autonomy",
                        "start experiment","end experiment",
                        "close", "cognitive trigger" ]
        if cmd in list_of_cmds:
            answer = self.write_read_socket(cmd)
        else:
            answer = "state not recognized"
        print("[Socket response to '{:}'] {:}".format(cmd, answer))

    def write_read_socket(self,x):
        data = "no response"
        if self.socket_connection is not None:
            self.socket_connection.send(x.encode())
            time.sleep(0.05)
            try:
                data = self.socket_connection.recv(1024).decode()
            except socket.timeout as e:
                print("Timeout error in socket")
                print(e)
                self.controller.running = False

        return data

    def arduino_command(self, cmd):
        if cmd == "turn on motors":
            answer = self.write_read_serial("1")
        elif cmd == "turn off motors":
            answer = self.write_read_serial("0")
        else:
            answer = "state not recognized"
        print("[Serial response to '{:}'] {:}".format(cmd, answer))

    def write_read_serial(self, x):
        data = "no response"
        if self.serial_connection is not None:
            self.serial_connection.write(bytes(x, encoding='utf8'))
            time.sleep(0.05)
            data = self.serial_connection.readline()

            data = data.decode('ascii')

        return data

    def run(self):
        """
        Finite state machine for the experiment
        1) waiting
        2) doing the task
        3) finished

        :return:
        """
        try:
            #Waiting until user press pedal
            while not self.counting and self.controller.running:
                time.sleep(0.5)

            self.start_signal()
            self.outlet.push_sample(["started", "{:0.3f}".format(time.time())])
            self.arduino_command("turn on motors")
            self.init_time = time.time()
            self.controller.task_state = "doing the task"

            self.socket_command("start experiment")
            if self.controller.args.autonomy:
                self.socket_command("turn on autonomy")

            while self.counting and self.controller.running:
                self.current_time = time.time() - self.init_time
                time.sleep(0.5)
                self.controller.time = self.current_time
                # print(self.current_time)

            self.end_signal()
            self.outlet.push_sample(["ended", "{:0.3f}".format(time.time())])
            self.arduino_command("turn off motors")
            #self.socket_command("turn off autonomy")
            self.socket_command("end experiment")
            self.controller.task_state = "finished"

            self.socket_command("close")
            if self.socket_connection is not None:
                self.socket_connection.close()
        except:

            self.controller.running = False
            traceback.print_exc()


    def start_signal(self):
        for _ in range(1):
            play_obj = self.start_sound.play()
            play_obj.wait_done()
            time.sleep(1)
    def end_signal(self):
        play_obj = self.end_sound.play()
        play_obj.wait_done()

    def listen_for_cognitive_predictions(self):
        count = 0
        while self.controller.running and self.controller.args.autonomy:
            streams = resolve_byprop('name', 'AssistantState', timeout=1)

            if len(streams) > 0:
                inlet = StreamInlet(streams[0])
                print("Cognitive state stream")
                while self.controller.running:
                    sample, timestamp = inlet.pull_sample(timeout=1)
                    #Logic to activate autonomy
                    if sample is not None:
                        print(sample, timestamp)
                        if sample[0] =='Suction':
                            #send autonomy command
                            self.start_signal()
                            self.socket_command("cognitive trigger")
                    time.sleep(0.1)
                print('Close listening socket')
            else:
                print(count, "AssistantState inlet not found. open real-time interface")
            count += 1
    def listen_mouse_events(self):
        count = 0
        while self.controller.running:
            streams = resolve_byprop('name', 'MouseButtons', timeout=1)

            if len(streams) > 0:
                inlet = StreamInlet(streams[0])
                print("oddball_speed stream found ")
                while self.controller.running:
                    sample, timestamp = inlet.pull_sample(timeout=1)

                    # mouse_event = "MouseButtonRight pressed"
                    mouse_event = "MouseButtonX2 pressed"
                    if timestamp is not None and sample[0] == mouse_event:
                        if time.time() - self.last_pressed > 3 :
                            self.last_pressed = time.time()
                            self.counting = not self.counting
                            print("got new speed %s at time %s" % (sample[0], timestamp))

                print('Close listening socket')
            else:
                print(count, "MouseButtons inlet not found")
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
