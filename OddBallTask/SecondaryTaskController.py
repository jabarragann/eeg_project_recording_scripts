import sys
sys.path.append('./../')
from OddBallTask.OddBallModule import OddBallModule
import threading

class Controller:
    def __init__(self):
        self.oddBallModule = OddBallModule(self,)
        self.running = False
        self.listenSpeedTh = threading.Thread(target=self.oddBallModule.listen_speed_markers)

    def run(self):
        self.running = True
        self.oddBallModule.start()
        self.listenSpeedTh.start()

        input("Press any key to close")
        self.running = False


if __name__ == '__main__':
    controllerMain = Controller()
    controllerMain.run()
    print("Finish task")