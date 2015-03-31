#-*- coding:utf-8 -*-

# Bachelorprojekt 2015 - Heartbeat-protokollen./

from __future__ import division
from socket import *
import time
import random
import os
import fcntl
import struct
import time
import sys

state = ""
broadcast_IP = '255.255.255.255'
broadcast_PORT = 54545

print ('Sending heartbeat to IP %s, port %d.\n') % (broadcast_IP, broadcast_PORT)


class heartbeat():
  def __init__(self):
    self.LTIMEOUT = 2
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    self.cs = cs
    self.state = "follower"
    

  def broadcast(self, data):
    self.cs.sendto(data, (broadcast_IP, broadcast_PORT))

    return 1

  def start(self):
    self.cs.bind( ('', broadcast_PORT))
    self.cs.setblocking(0)
    timer = time.time() + random.uniform(2.0, 5.0)
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("google.com",80))
    myIp = (s.getsockname()[0])
    castTimer = 0
    i = 0
    ipList = []
      
    while(True):
      if self.state == "leader":
        if i == 0:
           i = 1
        if castTimer < time.time():
          self.broadcast(str(ipList))
          
          castTimer = time.time() + 0.5 
        try:
          data, addr = sock.recvfrom(1024)
          magic = 1 
          if ipList == []:
             ipList.append([myIp, time.time() + self.LTIMEOUT]) #appender sig selv til at starte med.
          for sub in ipList: 
            if addr[0] in sub:
              sub[1] = time.time() + self.LTIMEOUT
              magic = 0
            if sub == ipList[len(ipList)-1] and magic: 
              ipList.append([addr[0], time.time() + self.LTIMEOUT])
          for sub in ipList:
            sys.stdout.write(sub[0] + " ")
          print ""
          for sub in ipList:
            if sub[0] == myIp:
               sub[1] = time.time() + self.LTIMEOUT
               break
            if sub == ipList[len(ipList)-1]:
               ipList.append([myIp, time.time() + self.LTIMEOUT])
        except:
         pass      
        for ip in ipList:
           if ip[1] < time.time():
             ipList.remove(ip) 
         
      elif self.state == "candidate":
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind( ("", 5005))
        sock.setblocking(0)

        voteCounter = 0 
        print "omg im a candidate, wuttup wid dat"
        self.broadcast("Vote")
        voteTime = time.time() + 2
        while(voteCounter <= ((len(ipList))/2)):
          if voteTime < time.time():
               self.state = "follower"
               timer = time.time() + random.uniform(2.0, 5.0)
               break
          try:
            message, addr = sock.recvfrom(1024)
            print message
            if message == "Voted":
               voteCounter += 1
               print voteCounter
          except:
            continue
        if self.state != "follower":
          self.state = "leader" 

      elif self.state == "follower":
          print "Leader-election in:", timer - time.time()
          if timer - time.time() < 0:
            self.state = "candidate"
            print "State set to: candidate"
          time.sleep(0.5)
          try:
            message, addr = self.cs.recvfrom(1024)
            print "Broadcast ip-address:",  addr
            if message == "Vote":
              s = socket(AF_INET, SOCK_DGRAM)
              s.sendto("Voted", (addr[0], 5005))
              print addr
            else:
              s = socket(AF_INET,SOCK_DGRAM)
              s.sendto("data", (addr[0], 5005))
            timer = timer.time() + random.uniform(2.0, 5.0)
          except:
            pass            
# Tester opgaven
def main():
  hb = heartbeat()
  hb.start()



# Sikrer sig at main metoden bliver eksekveret.
if __name__ == "__main__":
  main()




















