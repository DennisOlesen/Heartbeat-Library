from Heartbeat import Heartbeat
import time

hb = Heartbeat()

while(True):
  hb.set(hb.myIp, 0.8)
  time.sleep(100)
