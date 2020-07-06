import pyautogui as auto



codePath  = "C:\\Users\\asus\\PycharmProjects\\EEG-recording-lsl"

autoPath = "C:\\Users\\asus\\PycharmProjects\\EEG-recording-lsl\\automaticLaunch"
gtecLslPath = "C:\\Users\\asus\\Repos\\labstreaminglayer\\labstreaminglayer\\buildGNeedAccess\\install\\bin"

expSettingsPath = "C:\\Users\\asus\\Documents\\CurrentStudy\\Realtime-Project-Exp2\\exp-2-settings.cfg"

#commands
goToPath = "cd " + codePath
activateEnv = "conda activate eeg-env"

def setupTab(additionalCommand = None, arg=None):
	auto.write(goToPath, interval=0.02) 
	auto.press('enter')
	auto.write(activateEnv, interval=0.02) 
	auto.press('enter')

	#goto command
	if additionalCommand == 'goto' and arg is not None:
		auto.write("cd "+ arg, interval=0.02) 
		auto.press('enter')
	#Write 
	if additionalCommand == 'write' and arg is not None:
		auto.write(arg, interval=0.02)


if __name__ == '__main__':

	print(codePath)
	auto.sleep(5)

	#Get Active terminal
	fw = auto.getActiveWindow()
	fw.maximize()
	
	auto.hotkey('alt','shift','+', interval=0.2)
	auto.hotkey('alt','shift','+', interval=0.2)

	auto.hotkey('alt','left', interval=0.2)
	auto.hotkey('alt','left', interval=0.2)

	auto.hotkey('alt','shift','+', interval=0.2)
	auto.hotkey('alt','left', interval=0.2)
	auto.hotkey('alt','shift','-', interval=0.2)

	#Setup tab 1 - Timmer Tab
	setupTab(additionalCommand = "write", arg="python RecordExperiment.py 240")
	auto.hotkey('alt','up', interval=0.2)
	#Setup tab 2 - Automatic scripts
	setupTab(additionalCommand = "goto", arg=autoPath)
	auto.write("python organizeWindows.py")
	auto.hotkey('alt','right', interval=0.2)
	#Setup tab 3 - shimmer tab
	setupTab(additionalCommand = "write", arg="python SendShimmerLSL.py")
	auto.hotkey('alt','right', interval=0.2)
	#Setup tab 4 - lab recorder
	setupTab(additionalCommand = "write", arg="LabRecorder.exe -c "+expSettingsPath)
	auto.hotkey('alt','right', interval=0.2)
	#Setup tab 5 G.tec LSL
	setupTab(additionalCommand = "goto", arg=gtecLslPath)
	auto.write(".\\gNEEDaccess.exe", interval=0.02)