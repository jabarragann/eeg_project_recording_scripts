import time
import random
from pylsl import local_clock


for i in range(20):
    t1 = local_clock()
    t2 = time.time()
    print(t2 - t1)
    time.sleep(random.random() * 10)