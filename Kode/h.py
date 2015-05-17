from Heartbeat import Heartbeat
import time

myHb = Heartbeat()
timeS = time.time() + 3
for i in range(0, 10000):
  myHb.start()
myHb.set("eriks", "mor")

for i in range(0, 1000):
  myHb.start()
  time.sleep(1)
  print "yoloswag"
myHb.delete("eriks")

#print "eriksmor"
