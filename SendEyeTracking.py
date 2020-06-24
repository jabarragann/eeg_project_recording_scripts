
import time
import json
from tobiiglassesctrl import TobiiGlassesController
import datetime
from pylsl import StreamInfo, StreamOutlet, local_clock
import json

class StreamsObj:
	
	sf = 250 
	stream_channels = { 'gaze_position':['gidx','s','gpx','gpy'],
						'gaze_position_3d':['gidx','s','gp3dx','gp3dy','gp3dz'],
						'left_pupil_center': ['gidx','s','pcx','pcy','pcz'],
						'left_pupil_diameter':['gidx','s','pd'],
						'left_gaze_direction':['gidx','s','gdx','gdy','gdz'],
						'right_pupil_center': ['gidx','s','pcx','pcy','pcz'],
						'right_pupil_diameter':['gidx','s','pd'],
						'right_gaze_direction':['gidx','s','gdx','gdy','gdz']
					}

	stream_descriptions = { 'gaze_position':      ['gaze_position','2D coordinate',4, sf,'float32','gaze_position_lsl_id'],
							'gaze_position_3d':   ['gaze_position_3d','3D coordinate',5, sf,'float32','gaze_position__3d_lsl_id'],
							'left_pupil_center':  ['left_pupil_center','3D coordinate',5, sf,'float32','left_pupil_center_lsl_id'],
							'left_pupil_diameter':['left_pupil_diameter','mm',1, sf,'float32','left_pupil_diameter_lsl_id'],
							'left_gaze_direction':['left_gaze_direction','3D coordinate',5, sf,'float32','left_gaze_direction_lsl_id'],
							'right_pupil_center':  ['right_pupil_center','3D coordinate',5, sf,'float32','right_pupil_center_lsl_id'],
							'right_pupil_diameter':['right_pupil_diameter','mm',1, sf,'float32','right_pupil_diameter_lsl_id'],
							'right_gaze_direction':['right_gaze_direction','3D coordinate',5, sf,'float32','right_gaze_direction_lsl_id']
						  }

	def __init__(self):

		self.outlets_dict = {}

		#Iterate over all the stream names
		for key in stream_channels.keys():
			outlet = self.create_stream(key)
			self.outlets_dict[key] = outlet


	def create_stream(self, stream_name):
		#Configure LSL streams
		info = StreamInfo(*self.stream_descriptions[stream_name])

		# append channels meta-data
		channels = info.desc().append_child("channels")
		for c in stream_channels:
			if c == 'gidx':
			    channels.append_child("channel")\
			        .append_child_value("name", c)\
			        .append_child_value("unit", "na")\
			        .append_child_value("type", "marker")
			elif c == 's':
				channels.append_child("channel")\
			        .append_child_value("name", c)\
			        .append_child_value("unit", "na")\
			        .append_child_value("type", "marker")
			else:
				channels.append_child("channel")\
			        .append_child_value("name", c)\
			        .append_child_value("unit", "mm")\
			        .append_child_value("type", "coordinate")


		outlet = StreamOutlet(info)

		return outlet

	def sendData(self, name, data):
		if name == 'left_eye':
			data = data.replace("\'", "\"")
			data = json.loads(pos)

			# 'left_pupil_center': ['gidx','s','pcx','pcy','pcz'],
			d1 = data['pc']
			dataToSend = [d1['gidx'], d1['s']] + d1['pc']
			self.outlets_dict['left_pupil_center'].push_sample(dataToSend)
			
			# 'left_pupil_diameter':['gidx','s','pd'],
			d2 = data['pd']
			dataToSend = [d2['gidx'], d2['s'], d2['pd']] 
			self.outlets_dict['left_pupil_diameter'].push_sample(dataToSend)

			# 'left_gaze_direction':['gidx','s','gdx','gdy','gdz'],
			d3 = data['gd']
			dataToSend = [d3['gidx'], d3['s']] +d3['gd']
			self.outlets_dict['left_gaze_direction'].push_sample(dataToSend)
			
		elif name == 'right_eye':
			data = data.replace("\'", "\"")
			data = json.loads(pos)
			# 'right_pupil_center': ['gidx','s','pcx','pcy','pcz'],
			d1 = data['pc']
			dataToSend = [d1['gidx'], d1['s']] +d1['pc']
			self.outlets_dict['right_pupil_center'].push_sample(dataToSend)

			# 'right_pupil_diameter':['gidx','s','pd'],
			d2 = data['pd']
			dataToSend = [d2['gidx'], d2['s']] +d2['pd']
			self.outlets_dict['right_pupil_diameter'].push_sample(dataToSend)
			
			# 'right_gaze_direction':['gidx','s','gdx','gdy','gdz']
			d3 = data['gd']
			dataToSend = [d3['gidx'], d3['s']] +d3['gd']
			self.outlets_dict['right_gaze_direction'].push_sample(dataToSend)

		elif name == 'gp':
			#'gaze_position -- > ['gidx','s','gpx','gpy']
			data = data.replace("\'", "\"")
			data = json.loads(pos)
			dataToSend = [data['gidx'], data['s']] +data['gp']
			self.outlets_dict['gaze_position'].push_sample(dataToSend)

		elif name == 'gp3':
			#'gaze_position_3d':['gidx','s','gp3dx','gp3dy','gp3dz']
			data = data.replace("\'", "\"")
			data = json.loads(pos)
			dataToSend = [data['gidx'], data['s']] +data['gp3']
			self.outlets_dict['gaze_position_3d'].push_sample(dataToSend)

			


def printt(str1,file):
	
	print(str1)
	file.write(str1+"\n")

def calibration(tobiiglasses):
	if tobiiglasses.is_recording():
		rec_id = tobiiglasses.get_current_recording_id()
		tobiiglasses.stop_recording(rec_id)

	project_name = input("Please insert the project's name: ")
	project_id = tobiiglasses.create_project(project_name)

	participant_name = input("Please insert the participant's name: ")
	participant_id = tobiiglasses.create_participant(project_id, participant_name)

	calibration_id = tobiiglasses.create_calibration(project_id, participant_id)
	input("Put the calibration marker in front of the user, then press enter to calibrate")
	tobiiglasses.start_calibration(calibration_id)

	res = tobiiglasses.wait_until_calibration_is_done(calibration_id)

	if res is False:
		print("Calibration failed!")
		exit(1)



def main():

	#Configure LSL streams
	lsl_streams = StreamsObj()

	# #Data File
	# timestamp = '{:%Y-%b-%d %H-%M-%S}'.format(datetime.datetime.now())
	# file = open("./data/"+timestamp+'_data.txt','w')

	# #Create Tobii glasses Controller
	# tobiiglasses = TobiiGlassesController("192.168.71.50")
	# print(tobiiglasses.get_battery_status())

	# #Calibrate
	# calibration(tobiiglasses)

	
	# #Start Streaming
	# tobiiglasses.start_streaming()
	# print("Please wait ...")
	# time.sleep(3.0)

	# input("Press any key to start streaming")

	# while True:
	# 	try:
	# 		data = tobiiglasses.get_data()

	# 		StreamsObj.sendData('left_eye', data['left_eye'])
	# 		StreamsObj.sendData('right_eye', data['right_eye'])
	# 		StreamsObj.sendData('gp', data['gp'])
	# 		StreamsObj.sendData('gp3', data['gp3'])


	# 		printt(str(tobiiglasses.get_battery_status()),file)
	# 		printt("Head unit: %s" % tobiiglasses.get_data()['mems'],file)
	# 		printt("Left Eye: %s " % tobiiglasses.get_data()['left_eye'],file)
	# 		printt("Right Eye: %s " % tobiiglasses.get_data()['right_eye'],file)
	# 		printt("Gaze Position: %s " % tobiiglasses.get_data()['gp'],file)
	# 		printt("Gaze Position 3D: %s " % tobiiglasses.get_data()['gp3'],file)
	# 	except Exception as e:

	# 		print(e)
	# 		print("Closing Tobii")
	# 		file.close()
	# 		tobiiglasses.stop_streaming()
	# 		tobiiglasses.close()

	# 		break

	# print("Closing programme")

if __name__ == '__main__':
    main()
