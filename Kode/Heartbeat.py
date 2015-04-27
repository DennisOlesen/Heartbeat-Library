#-*- coding:utf-8 -*-

# Bachelorprojekt 2015 - Heartbeat-protokollen.

from __future__ import division
from socket import *
import time, random, os, sys
import thread, SimpleHTTPServer, SocketServer
import Log
state = ""
broadcast_IP = '255.255.255.255'
broadcast_PORT = 54545
LTIMEOUT = 2

print ('Sending heartbeat to IP %s, port %d.\n') % (broadcast_IP, broadcast_PORT)

class heartbeat():
  """
  Klasse for heartbeat-protokollen.
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
    thread.start_new_thread(mySimpleServer, (8080,))
    """
    Starter heartbeat-protokollen.
    """
    timer = time.time() + random.uniform(2.0, 5.0)

    # Finder frem til ip-adressen for maskinen, så det virker på linux.
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("google.com", 80))
    myIp = (s.getsockname()[0])
    ipLog = Log.log() 
    castTimer = 0
    ipList = []
    tLastVote = 0
    message = ""
    currentKey = -1
    expectedResponses = 1
    while(True):
    # Lederen er ansvarlig for at opdatere loggen løbende via Heartbeats.
      if self.state == "leader":
        if len(ipLog.getList()) != len(ipList):
           ipList = []
           for sub in ipLog.getList():
             ipList.append(sub, time.time() + LTIMEOUT)
        if castTimer < time.time():
          #hvis der er lige så mange som forventet, comitter vi. 
          if expectedResponses == 0:
             print "Commiting"
             print ipList
             print ipLog.getLog()
             ipLog.commit(currentKey)
             message = message + " co:" + str(currentKey)
             
          print ipLog.getKey()
          print ipLog.getLog()
          # Opdaterer loggen
          expectedResponses = len(ipList)-1
          self.broadcast(str(ipLog.getKey()) + "," + message)
          currentKey = ipLog.getKey()
          message = ""
          castTimer = time.time() + 0.5

        try:
          data, addr = sock.recvfrom(1024)
          if (data == "Voted"):
            pass
          else:
            print message 
            if (int(data) == currentKey-1):
               expectedResponses -= 1 
             
            if (int(data) < ipLog.getLowestKey()):
              s = socket(AF_INET,SOCK_DGRAM)
              print "magic"
              s.sendto("ow:" + str(ipLog.getLog()) + "," + str(ipLog.getList()), (addr[0], 5005))
              print "trick"


            if (int(data) != currentKey ):
              #Tjekker hvis en følger er bagud, sender bagud data
              upToDateData = ipLog.compile(data)
              s = socket(AF_INET,SOCK_DGRAM)
              s.sendto(upToDateData, (addr[0], 5005))

            elemNotSet = 1 # Til at checke om elementer er blevet placeret

            # Opdaterer værdier for følgerne
            for sub in ipList:
              if addr[0] in sub:
                sub[1] = time.time() + LTIMEOUT
                elemNotSet = 0
              if sub == ipList[len(ipList)-1] and elemNotSet:
                ipList.append([addr[0], time.time() + LTIMEOUT])
                message = message + " ad:" + str(addr[0])
                print message
                ipLog.add(addr[0])

           # Printer en oversigt over IP-adresser samt
            for sub in ipList:
              print "[" + str(sub[0]) + "]"
        except:
          pass
        # Appender sig selv til at starte med.
        if ipList == []:
          ipList.append([myIp, time.time() + LTIMEOUT])
          message = message + " ad:" + str(myIp)
          print message
          ipLog.add(myIp)


         # Opdaterer værdier for lederen
        for sub in ipList:
          if sub[0] == myIp:
             sub[1] = time.time() + LTIMEOUT
             break
          if sub == ipList[len(ipList)-1]:
             ipList.append([myIp, time.time() + LTIMEOUT])
             message = message + " ad:" + str(myIp)
             print message
             ipList.add(myIp)

        for ip in ipList:
           if ip[1] < time.time():
             ipList.remove(ip)
             message = message + " re:" + str(ip[0])
             ipLog.remove(ip[0])


      elif self.state == "candidate":
      # Kandidaten er overgangsstadiet mellem følger og leder.
      # Den opretter en afstemning for at blive den nye leder.
            # Votecounter starter på 1,
      # da en kandidat altid stemmer på sig selv.
        voteCounter = 1
        self.broadcast("Vote")
        # Laver en voteTime, for at sikre sig at
        # den ikke venter på stemmer forevigt.
        voteTime = time.time() + LTIMEOUT
        while(voteCounter <= ((len(ipList))/2)):
          # Returnerer til følger hvis der ikke er stemmer nok
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
        # Bliver leder hvis der er stemmer nok til at komme ud
        # af løkken, og endnu ikke er blevet følger.
        if self.state != "follower":
          voteCounter = 0
          self.state = "leader"
          print "State set to: leader"

      elif self.state == "follower":
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind( ("", 5005))
        sock.setblocking(0)

        # Følgeren lytter på og besvarer lederens forspørgsler,
        # samt skifter til kandidat hvis den ikke hører fra lederen.
        print "Leader-election in:", timer - time.time()
        try:
          data, addr = sock.recvfrom(1024)
          ipLog.parse(data)
        except:
          pass  
 
        try:
          message, addr = self.b_sock.recvfrom(1024)
          print "Broadcast ip-address:",  addr
          # Stemmer på kandidat hvis den modtager besked.
          # Stemmer kun 1 gang per valg.
          if message == "Vote" and tLastVote < time.time():
            tLastVote = time.time() + LTIMEOUT
            s = socket(AF_INET, SOCK_DGRAM)
            s.sendto("Voted", (addr[0], 5005))
          else:
            # Svarer på lederens heartbeat.
           # Opdaterer loggen
            splittext = message.split(",")
            print ipLog.getLog()
            print ipList
            key = splittext[0]
            msg = splittext[1]
            if ipLog.getKey() == int(key):
               ipLog.parse(msg)
            s = socket(AF_INET,SOCK_DGRAM)
            s.sendto(str(ipLog.getKey()), (addr[0], 5005))
 
          timer = time.time() + random.uniform(2.0, 5.0)
        except:
          pass
        # Bliver kandidat hvis der ikke modtages besked fra lederen.
        if timer - time.time() < 0:
          self.state = "candidate"
          print "State set to: candidate"
        time.sleep(0.5)


def mySimpleServer(port):
  Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

  httpd = SocketServer.TCPServer(("", port), Handler)

  print "serving at port", port
  httpd.serve_forever()

# Tester opgaven
def main():
  hb = heartbeat()
  hb.start()



# Sikrer sig at main metoden bliver eksekveret.
if __name__ == "__main__":
  main()
