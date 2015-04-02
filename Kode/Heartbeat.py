#-*- coding:utf-8 -*-

# Bachelorprojekt 2015 - Heartbeat-protokollen./

from __future__ import division
from socket import *
import time, random, os, sys


state = ""
broadcast_IP = '255.255.255.255'
broadcast_PORT = 54545
LTIMEOUT = 2

print ('Sending heartbeat to IP %s, port %d.\n') % (broadcast_IP, broadcast_PORT)

class heartbeat():
  """
  Klasse for heartbeat-protokollen, der so fare kan håndtere 
  Discovery samt leader election
  """
   
  def __init__(self):
    """
    Initialiserer klassen.
    Sætter vores socket, så vi kan sende data til det senere.
    Sætter alle medlemmers state til follower.
    """
    b_sock = socket(AF_INET, SOCK_DGRAM)
    b_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    b_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    b_sock.bind( ('', broadcast_PORT))
    b_sock.setblocking(0)
    self.b_sock = b_sock
    self.state = "follower"
    

  def broadcast(self, data):
    """
    Sender data ud til en given broadcast IP og PORT.
    """
    self.b_sock.sendto(data, (broadcast_IP, broadcast_PORT))


  def start(self):
    """
    Starter heartbeat-protokollen.
    """
    timer = time.time() + random.uniform(2.0, 5.0)
    
    # Finder frem til ip-adressen for maskinen, så det virker på linux.
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("google.com", 80))
    myIp = (s.getsockname()[0])
    
    castTimer = 0
    ipList = []
    tLastVote = 0
      
    while(True):
      if self.state == "leader":
        if castTimer < time.time():
          self.broadcast(str(ipList))
          castTimer = time.time() + 0.5 
        
        try:
          data, addr = sock.recvfrom(1024)
          elemNotSet = 1 # Til at checke om elementer er blevet placeret
          
          # Appender sig selv til at starte med.
          if ipList == []:
           ipList.append([myIp, time.time() + LTIMEOUT]) 
          
          for sub in ipList: 
            if addr[0] in sub:
              sub[1] = time.time() + LTIMEOUT
              elemNotSet = 0
            if sub == ipList[len(ipList)-1] and elemNotSet: 
              ipList.append([addr[0], time.time() + LTIMEOUT])
          #######################################
          for sub in ipList:
            sys.stdout.write(sub[0] + " ")
          print ""
          #######################################
          for sub in ipList:
            if sub[0] == myIp:
              sub[1] = time.time() + LTIMEOUT
              break
            if sub == ipList[len(ipList)-1]:
              ipList.append([myIp, time.time() + LTIMEOUT])
        except:
         pass      
        for ip in ipList:
           if ip[1] < time.time():
             ipList.remove(ip) 
         
      elif self.state == "candidate":
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind( ("", 5005))
        sock.setblocking(0)

        voteCounter = 1 
        self.broadcast("Vote")
        voteTime = time.time() + LTIMEOUT
        while(voteCounter <= ((len(ipList))/2)):
          if voteTime < time.time():
            self.state = "follower"
            voteCounter = 0
            timer = time.time() + random.uniform(2.0, 5.0)
            break
          try:
            message, addr = sock.recvfrom(1024)
            print message
            if message == "Voted":
              voteCounter += 1
              print voteCounter
          except:
            pass 
        if self.state != "follower":
          voteCounter = 0
          self.state = "leader" 
          print "State set to: leader"

      elif self.state == "follower":
        print "Leader-election in:", timer - time.time()
        try:
          message, addr = self.b_sock.recvfrom(1024)
          print "Broadcast ip-address:",  addr
          if message == "Vote" and tLastVote < time.time():
            tLastVote = time.time() + LTIMEOUT
            s = socket(AF_INET, SOCK_DGRAM)
            s.sendto("Voted", (addr[0], 5005))
            print addr
          else:
            s = socket(AF_INET,SOCK_DGRAM)
            s.sendto("data", (addr[0], 5005))
            # Opdaterer loggen
            ipList = eval(message) 
          timer = time.time() + random.uniform(2.0, 5.0)
        except:
          pass            
        if timer - time.time() < 0:
          self.state = "candidate"
          print "State set to: candidate"
        time.sleep(0.5)
 
# Tester opgaven
def main():
  hb = heartbeat()
  hb.start()



# Sikrer sig at main metoden bliver eksekveret.
if __name__ == "__main__":
  main()














