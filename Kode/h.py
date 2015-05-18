from Heartbeat import Heartbeat
import time
import psutil
from socket import *


s = socket(AF_INET, SOCK_DGRAM)
s.connect(("google.com", 80))
myIp = (s.getsockname()[0])
s = None
ipList = []
whiteList = []
hb = Heartbeat()
timeS = time.time() + 3
#Asserts that we're a member, prior to sending requests.
for i in range(0, 10000):
  hb.start()

while(1):
 if (hb.getState() == "follower"):
  hb.start()
  time.sleep(100)
  cpuLoad = psutil.cpu_percent()
  hb.set(myIp, cpuLoad)

 elif (hb.getState() == "candidate"):
  hb.start
 
 elif (hb.getState() == "leader"):
  #cpuLoad = psutil.cpu_percent()
  #hb.set(myIp, cpuLoad)
  hb.start()
  ipList = hb.getIps()
  print ipList
  print hb.getDic()
  for ip in ipList:
    if ip != myIp:
      if hb.get(str(ip)) < 0.8:
        if ip not in whiteList:
          whiteList.append(ip)
      elif ip in whiteList:
        whiteList.remove(ip)
  print whiteList


#print "eriksmor"
