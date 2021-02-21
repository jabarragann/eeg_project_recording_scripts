import pyautogui as auto

codePath = "C:\\Users\\asus\\PycharmProjects\\EEG-recording-lsl"

autoPath = "C:\\Users\\asus\\PycharmProjects\\EEG-recording-lsl\\automaticLaunch"
gtecLslPath = "C:\\Users\\asus\\Repos\\labstreaminglayer\\labstreaminglayer\\buildGNeedAccess\\install\\bin"

expSettingsPath = r"C:\Users\asus\Documents\CurrentStudy\Realtime-Project-Phase4\exp-4-settings.cfg"
#"C:\\Users\\asus\\Documents\\CurrentStudy\\Realtime-Project-Exp2\\exp-2-settings.cfg"

expControllerPath = r"C:\Users\asus\PycharmProjects\EEG-recording-lsl\OddBallTask"

mouseRecorderPath = r"C:\Users\asus\Repos\labstreaminglayer\compiled-bin"

# commands
goToPath = "cd " + codePath
activateEnv = "conda activate eeg-env"


def setupTab(additionalCommand=None, arg=None, goto_code_base=True):
    if goto_code_base:
        auto.write(goToPath, interval=interval_writing)
        auto.press('enter')

    auto.write(activateEnv, interval=interval_writing)
    auto.press('enter')

    # goto command
    if additionalCommand == 'goto' and arg is not None:
        auto.write("cd " + arg, interval=interval_writing)
        auto.press('enter')
    # Write
    if additionalCommand == 'write' and arg is not None:
        auto.write(arg, interval=interval_writing)


if __name__ == '__main__':
    interval_writing = 0.018
    print(codePath)
    auto.sleep(0.5)

    # Get Active terminal
    fw = auto.getActiveWindow()
    fw.maximize()

    auto.hotkey('alt', 'shift', '-', interval=interval_writing)
    auto.hotkey('alt', 'shift', '-', interval=interval_writing)

    auto.hotkey('alt', 'up', interval=interval_writing)
    auto.hotkey('alt', 'up', interval=interval_writing)

    auto.hotkey('alt', 'shift', '-', interval=interval_writing)
    auto.hotkey('alt', 'up', interval=interval_writing)

    auto.hotkey('alt', 'shift', '+', interval=interval_writing)
    auto.hotkey('alt', 'down', interval=interval_writing)
    auto.hotkey('alt', 'shift', '+', interval=interval_writing)

    auto.hotkey('alt', 'up', interval=interval_writing)
    setupTab(additionalCommand="goto", arg=mouseRecorderPath, goto_code_base=False)
    setupTab(additionalCommand="write", arg="MouseRecorder.exe",goto_code_base=False)

    auto.hotkey('alt', 'right', interval=interval_writing)
    setupTab(additionalCommand="goto", arg=autoPath)
    auto.write("python organizeWindows.py")

    auto.hotkey('alt', 'down', interval=interval_writing)
    setupTab(additionalCommand="write", arg="python SendGnautilusAlternative.py")

    auto.hotkey('alt', 'right', interval=interval_writing)
    setupTab(additionalCommand="write", arg="python SendShimmerLSL.py")

    auto.hotkey('alt', 'down', interval=interval_writing)
    setupTab(additionalCommand="write", arg="LabRecorder.exe -c " + expSettingsPath, goto_code_base=False)

    auto.hotkey('alt', 'down', interval=interval_writing)
    setupTab(additionalCommand="goto", arg=expControllerPath)
    setupTab(additionalCommand="write", arg="python ExperimentController.py 180", goto_code_base=False)

