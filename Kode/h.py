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

while(1):

 print "abc"
 if (hb.getState() == "follower"):
  time.sleep(100)
  cpuLoad = psutil.cpu_percent()
  hb.set(myIp, cpuLoad)

 elif (hb.getState() == "candidate"):
  pass 
 elif (hb.getState() == "leader"):
  #cpuLoad = psutil.cpu_percent()
  #hb.set(myIp, cpuLoad)
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

  hb.set('abc', 1)


#print "eriksmor"
