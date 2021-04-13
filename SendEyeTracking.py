
import time
import json
from tobiiglassesctrl import TobiiGlassesController
import datetime
from pylsl import StreamInfo, StreamOutlet, local_clock
import json
import traceback

class StreamsObj:

	#Irregular stream of data
	sf = 0
	stream_channels = { 'gaze_position':['gidx','s','gpx','gpy'],
						'gaze_position_3d':['gidx','s','gp3dx','gp3dy','gp3dz'],
						'left_eye_data': ['gidx','s','pcx','pcy','pcz','pd','gdx','gdy','gdz'],
						'right_eye_data': ['gidx','s','pcx','pcy','pcz','pd','gdx','gdy','gdz'],
						'mems': ['acx','acy','acz','gyx','gyy','gyz']
					  }

	# stream_channels = {'gaze_position': ['gidx', 's', 'gpx', 'gpy'],
	# 				   'left_eye_data': ['gidx', 's','pd'],
	# 				   'right_eye_data': ['gidx', 's', 'pd'],
	# 				   'mems': ['acx', 'acy', 'acz', 'gyx', 'gyy', 'gyz']}

	stream_descriptions = { 'gaze_position':      ['gaze_position','eye_tracker',4, sf,'float32','gaze_position_lsl_id'],
							'gaze_position_3d':   ['gaze_position_3d','eye_tracker',5, sf,'float32','gaze_position__3d_lsl_id'],
							'left_eye_data':  ['left_eye_data','eye_tracker',9, sf,'float32','left_eye_data_lsl_id'],
							'right_eye_data':  ['right_eye_data','eye_tracker',9, sf,'float32','right_eye_data_lsl_id'],
							'mems' : ['accelerometer_gyro_tobii', 'eye_tracker',6,sf,'float32','accelerometer_gyro__lsl_id']
						  }

	def __init__(self):

		self.outlets_dict = {}

		#Iterate over all the stream names
		for key in self.stream_channels.keys():
			outlet = self.create_stream(key)
			self.outlets_dict[key] = outlet


	def create_stream(self, stream_name):
		#Configure LSL streams
		info = StreamInfo(*self.stream_descriptions[stream_name])

		# append channels meta-data
		channels = info.desc().append_child("channels")
		for c in self.stream_channels[stream_name]:
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
			# 'left_eye_data': ['gidx','s','pcx','pcy','pcz','pd','gdx','gdy','gdz']
			d1 = data['pc']
			d2 = data['pd']
			d3 = data['gd']
			
			dataToSend = [d1['gidx'], d1['s']] + d1['pc'] + [ d2['pd']] + d3['gd']
			self.outlets_dict['left_eye_data'].push_sample(dataToSend)
			
		elif name == 'right_eye':
			# 'right_eye_data': ['gidx','s','pcx','pcy','pcz','pd','gdx','gdy','gdz'],
			d1 = data['pc']
			d2 = data['pd']
			d3 = data['gd']

			dataToSend = [d1['gidx'], d1['s']] + d1['pc'] + [ d2['pd']] + d3['gd']
			self.outlets_dict['right_eye_data'].push_sample(dataToSend)

		elif name == 'gp':
			#'gaze_position -- > ['gidx','s','gpx','gpy']
			dataToSend = [data['gidx'], data['s']] +data['gp']
			self.outlets_dict['gaze_position'].push_sample(dataToSend)

		elif name == 'gp3':
			#'gaze_position_3d':['gidx','s','gp3dx','gp3dy','gp3dz']
			dataToSend = [data['gidx'], data['s']] +data['gp3']
			self.outlets_dict['gaze_position_3d'].push_sample(dataToSend)

		elif name ==  'mems':
			ac_data = data['ac']
			gy_data = data['gy']
			dataToSend = [] + ac_data['ac'] + gy_data['gy']
			self.outlets_dict['mems'].push_sample(dataToSend)


			

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

	#Data File
	timestamp = '{:%Y-%b-%d %H-%M-%S}'.format(datetime.datetime.now())
	file = open("./data/"+timestamp+'_data.txt','w')

	#Create Tobii glasses Controller
	tobiiglasses = TobiiGlassesController("192.168.71.50")
	print("Sampling frequency: ",  tobiiglasses.get_et_freq())
	print(tobiiglasses.get_battery_status())

	#Calibrate
	# calibration(tobiiglasses)

	#Start Streaming
	tobiiglasses.start_streaming()
	print("Please wait ...")
	time.sleep(3.0)

	input("Press any key to start streaming")

	current_gidx = -9999

	startTime = time.time()
	old_time = time.time()
	time.sleep(0.1)
	try:
		while True:
				
				data = tobiiglasses.get_data()
				
				#Send data to LSL only there is a new data point
				if current_gidx < data['gp']['gidx']:
					current_gidx = data['gp']['gidx']
					print(data['gp'])
					#Send data
					lsl_streams.sendData('left_eye', data['left_eye'])
					lsl_streams.sendData('right_eye', data['right_eye'])
					lsl_streams.sendData('gp', data['gp'])
					lsl_streams.sendData('gp3', data['gp3'])

					#Print Battery status
					# print(tobiiglasses.get_battery_status())

				if time.time() - old_time > 0.02: #Send data every 20ms
					lsl_streams.sendData('mems',data['mems'])
					old_time = time.time()
					
	except Exception as e:
		print(e)
		print("Closing Tobii")
		trace =  traceback.format_exc()
		print(trace)
	
	finally:
		file.close()
		tobiiglasses.stop_streaming()
		tobiiglasses.close()	
		

	print("Closing programme")

if __name__ == '__main__':
    main()
