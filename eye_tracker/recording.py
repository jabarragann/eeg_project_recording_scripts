# print("Sending markers...")
# markernames = ['started','ended']
#
# startTime = time.time()
# outlet.push_sample(["started"])
#
# tempBeeps = 0
# prevTime = time.time()
# while time.time()-startTime < totalDuration:
#     tempBeeps += time.time() - prevTime
#     prevTime = time.time()
#
#     if tempBeeps > 60:
#         print("Experiment time ",time.time()-startTime)
#         tempBeeps = 0
#         play_obj = startSound.play()
#         play_obj.wait_done()
#
#     time.sleep(0.1)
#
# outlet.push_sample(["ended"])
# play_obj = endSound.play()
# play_obj.wait_done()
#
# print("Experiment finished. Remember to stop data recording")
#
# print("Start time", startTime)