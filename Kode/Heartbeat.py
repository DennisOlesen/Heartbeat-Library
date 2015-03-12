#-*- coding:utf-8 -*-

# Bachelorprojekt 2015 - Heartbeat-protokollen.
# Dennis Bøgelund Olesen & Erik David Allin

from __future__ import division
from socket import *
import time
import random
import os
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
    while(True):
      if self.state == "leader":
        self.broadcast("Hello followers")
        data = self.cs.recv(1024)
        time.sleep(0.5)

        if data != "Hello followers":
         print str(data)

      elif self.state == "candidate":
        self.broadcast("Anarchy")

      elif self.state == "follower":
          print timer
          if timer == 0:
            self.state = "leader"
            print "I'm a leader"

          try:
            if self.cs.recv(1024) == "Hello followers":
              self.broadcast("Follower says: Hello leader")
              timer = random.randint(5, 20)
          except:
            timer -= 1
            time.sleep(0.5)

# Tester opgaven
def main():
  hb = heartbeat()
  hb.start()



# Sikrer sig at main metoden bliver eksekveret.
if __name__ == "__main__":
  main()
