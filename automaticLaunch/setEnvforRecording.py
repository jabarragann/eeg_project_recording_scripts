import pyautogui as auto



codePath  = "C:\\Users\\asus\\PycharmProjects\\EEG-recording-lsl"

autoPath = "C:\\Users\\asus\\PycharmProjects\\EEG-recording-lsl\\automaticLaunch"
gtecLslPath = "C:\\Users\\asus\\Repos\\labstreaminglayer\\labstreaminglayer\\buildGNeedAccess\\install\\bin"

expSettingsPath = "C:\\Users\\asus\\Documents\\CurrentStudy\\Realtime-Project-Exp2\\exp-2-settings.cfg"

#commands
goToPath = "cd " + codePath
activateEnv = "conda activate eeg-env"

def setupTab(additionalCommand = None, arg=None):
	auto.write(goToPath, interval=interval_writing)
	auto.press('enter')
	auto.write(activateEnv, interval=interval_writing)
	auto.press('enter')

	#goto command
	if additionalCommand == 'goto' and arg is not None:
		auto.write("cd "+ arg, interval=interval_writing)
		auto.press('enter')
	#Write 
	if additionalCommand == 'write' and arg is not None:
		auto.write(arg, interval=interval_writing)


if __name__ == '__main__':
	interval_writing = 0.02
	print(codePath)
	auto.sleep(1)

	#Get Active terminal
	fw = auto.getActiveWindow()
	fw.maximize()
	
	auto.hotkey('alt','shift','+', interval=interval_writing)
	auto.hotkey('alt','shift','+', interval=interval_writing)

	auto.hotkey('alt','left', interval=interval_writing)
	auto.hotkey('alt','left', interval=interval_writing)

	auto.hotkey('alt','shift','+', interval=interval_writing)
	auto.hotkey('alt','left', interval=interval_writing)
	auto.hotkey('alt','shift','-', interval=interval_writing)

	#Setup tab 1 - Timmer Tab
	setupTab(additionalCommand = "write", arg="python RecordExperiment.py 180")
	auto.hotkey('alt','up', interval=interval_writing)
	#Setup tab 2 - Automatic scripts
	setupTab(additionalCommand = "goto", arg=autoPath)
	auto.write("python organizeWindows.py")
	auto.hotkey('alt','right', interval=interval_writing)
	#Setup tab 3 - shimmer tab
	setupTab(additionalCommand = "write", arg="python SendShimmerLSL.py")
	auto.hotkey('alt','right', interval=interval_writing)
	#Setup tab 4 - lab recorder
	setupTab(additionalCommand = "write", arg="LabRecorder.exe -c " + expSettingsPath)
	auto.hotkey('alt','right', interval=interval_writing)
	#Setup tab 5 G.tec LSL
	setupTab(additionalCommand = "write", arg="python SendGnautilusLSL.py")
	auto.hotkey('alt','right', interval=interval_writing)
	# setupTab(additionalCommand = "goto", arg=gtecLslPath)
	# auto.write(".\\gNEEDaccess.exe", interval=interval_writing)