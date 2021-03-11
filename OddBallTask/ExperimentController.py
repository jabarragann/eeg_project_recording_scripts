import sys
sys.path.append('./../')
# from OddBallTask.OddBallModule import OddBallModule
from OddBallTask.OddBallModuleModification import OddBallModule
import threading
from OddBallTask.Timer import OpencvTimer

class Controller:
    def __init__(self):
        self.oddBallModule = OddBallModule(self,)
        self.timerModule = OpencvTimer(self,)
        self.running = False
        self.controller_secondary_on = False

        self.listenSpeedTh = threading.Thread(target=self.oddBallModule.listen_speed_markers)


    def run(self):
        self.running = True
        self.oddBallModule.start()
        self.listenSpeedTh.start()
        self.timerModule.start()

        # input("Press any key to close")
        # self.running = False


if __name__ == '__main__':
    controllerMain = Controller()
    controllerMain.run()
    print("Finish task")