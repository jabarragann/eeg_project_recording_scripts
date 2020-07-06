import pyautogui as auto
import time

windowDict = {"BrainVision LSL Viewer":None,
			  "Figure 1: LSL:Stream'Shimmer_ppg'":None,
			  "Figure 2: LSL:Stream'Shimmer_gsr'":None,
			  "Experiment timer": None,
			  "Lab Recorder": None
			  }

windowParameters =  { "BrainVision LSL Viewer":{"topLeft":[320,0],"width":1624,"height":700,'activate':False},
					  "Figure 1: LSL:Stream'Shimmer_ppg'":{"topLeft":[-34,0],"width":396,"height":546,'activate':True},
					  "Figure 2: LSL:Stream'Shimmer_gsr'":{"topLeft":[-34,532],"width":396,"height":513,'activate':True},
					  "Experiment timer": {"topLeft":[1507,670],"width":420,"height":375,'activate':True},
					  "Lab Recorder": {"topLeft":[838, 670],"width":684,"height":375,'activate':True}
					}

if __name__ == "__main__":

	windows = auto.getAllWindows() 

	for w1 in windows:
		# print(w.title)
		if w1.title in windowDict.keys():
			
			windowDict[w1.title] = w1

	for name,w1 in windowDict.items():
		if w1 is not None:
			print(name)
			print("top left", w1.topleft)
			print("width",  w1.width)
			print("height", w1.height)

			#Move to default positions
			w1.minimize()
			w1.restore()
			x,y = windowParameters[name]['topLeft'][0],windowParameters[name]['topLeft'][1]
			w1.moveTo(x,y)
			w,h = windowParameters[name]['width'],windowParameters[name]['height']
			w1.resizeTo(w,h)