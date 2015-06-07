# LoadBalancing.py

from Heartbeat import Heartbeat
import time
import random
hb = Heartbeat()
available_ips = []

while(True):
  if hb.getState() == "follower":
    hb.set(hb.myIp, random.random())
    time.sleep(1)

  if hb.getState() == "leader":
    tmpDic = hb.getDic()
    available_ips = []

    for key in tmpDic:
      if tmpDic[key] < 0.8:
         available_ips.append(key)
    time.sleep(1)
    print "Available IPs:", available_ips
  #Send available_ips to router