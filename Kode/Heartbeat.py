#-*- coding:utf-8 -*-

# Bachelorprojekt 2015 - Heartbeat-protokollen.
# Dennis Bøgelund Olesen & Erik David Allin

from __future__ import division
from socket import *
import time
import random
import os
import fcntl
import struct

state = ""
broadcast_IP = '255.255.255.255'
broadcast_PORT = 54545

print ('Sending heartbeat to IP %s, port %d.\n') % (broadcast_IP, broadcast_PORT)


class heartbeat():
  def __init__(self):
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
    timer = random.randint(5, 20)
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("google.com",80))
    myIp = (s.getsockname()[0])
   
    i = 0
    ipList = []
      
    while(True):
      if self.state == "leader":
        if i == 0:
          sock = socket(AF_INET, SOCK_DGRAM)
          sock.bind( ("", 5005))
          sock.setblocking(0)
          i = 1
        self.broadcast(myIp)
        try:
          data, addr = sock.recvfrom(1024)
          if addr[0] not in ipList:
            ipList.append(addr[0])
            print ipList
        except:
          print "No data recieved"
        time.sleep(0.5)
      
      elif self.state == "candidate":
        self.broadcast("Anarchy")

      elif self.state == "follower":
          print "Leader-election in:", timer
          if timer == 0:
            self.state = "leader"
            print "State set to: Leader"
          time.sleep(0.5)
          try:
            message = self.cs.recv(1024)
            print "Broadcast ip-address:",  message
            if message != "":
              s = socket(AF_INET,SOCK_DGRAM)
              s.sendto("data", (message,5005))
              timer = random.randint(5, 20)
          except:
            timer -= 1
            
# Tester opgaven
def main():
  hb = heartbeat()
  hb.start()



# Sikrer sig at main metoden bliver eksekveret.
if __name__ == "__main__":
  main()
