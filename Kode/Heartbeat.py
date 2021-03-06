#-*- coding:utf-8 -*-

# Bachelorprojekt 2015 - Heartbeat-protokollen.

from __future__ import division
from socket import *
import time, random, os, sys
import thread, SimpleHTTPServer, SocketServer
import Log
import traceback

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
    #print "broadcast send:", data
    self.b_sock.sendto(data, (broadcast_IP, broadcast_PORT))
    #print data

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
    s = None

    ipLog = Log.log() 
    castTimer = 0
    ipList = []
    tLastVote = 0
    message = ""
    currentKey = -1
    expectedResponses = 1

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind( ("", 5005))
    sock.setblocking(0)

    while(True):
    # Lederen er ansvarlig for at opdatere loggen løbende via Heartbeats.
      if self.state == "leader":
        if len(ipLog.getList()) != len(ipList):
           ipList = []
           for sub in ipLog.getList():
             ipList.append([sub, time.time() + LTIMEOUT])
        if castTimer < time.time():
          # Hvis der er lige så mange som forventet, comitter vi. 
          if expectedResponses == 0 and len(ipLog.getLog()) != 0:
             print "Commiting"
             ipLog.commit(currentKey)
             message = message + " co:" + str(currentKey)
             
          #print ipLog.getKey()
          print "Log: " ,  ipLog.getLog()
          print "List: " , ipLog.getList()
          # Opdaterer loggen
          if len(ipList) > 1:
            expectedResponses = len(ipList)-1
          else:
            expectedResponses = 1
          self.broadcast(str(ipLog.getKey()-1) + "," + message)
          print "Key, message: " , ipLog.getKey()-1, message
          currentKey = ipLog.getKey()
          message = ""
          castTimer = time.time() + 0.5
        try:
          data, addr = sock.recvfrom(1024)
          print "svar far hb: " , data , " ok?"
          #print "xxxxxxxxxxxxxxxxxxxxx"
          if (data == "Voted"):
            pass
          else:
            #print message 
            if (int(data) == currentKey):
               expectedResponses -= 1 
            print "OW?: " , data, "<", ipLog.getLowestKey() , "ow?"
             
            if (int(data) < int(ipLog.getLowestKey()) or int(data) > currentKey):
              #s = socket(AF_INET,SOCK_DGRAM)
              #print "magic"
              sock.sendto("ow:" + str(ipLog.getLog()) + "-" + str(ipLog.getList()), (addr[0], 5005))
            print "currentKey: " , currentKey , " ok?"
            if (int(data) < currentKey and int(data) != -1):
              #Tjekker hvis en følger er bagud, sender bagud data
              print "Pakker upToDateData"
              upToDateData = ipLog.compile(int(data))
   
              #print "Sending", upToDateData, "..."
              #s = socket(AF_INET,SOCK_DGRAM)
              sock.sendto(upToDateData, (addr[0], 5005))
              print "Data er sendt: " , upToDateData

            elemNotSet = 1 # Til at checke om elementer er blevet placeret

            # Opdaterer værdier for følgerne
            for sub in ipList:
              if addr[0] in sub:
                sub[1] = time.time() + LTIMEOUT
                elemNotSet = 0
                print sub
              if sub == ipList[len(ipList)-1] and elemNotSet:
                ipList.append([addr[0], time.time() + LTIMEOUT])
                message = message + " ad:" + str(addr[0])
                #print message
                ipLog.add(addr[0])

           # Printer en oversigt over IP-adresser samt
            #for sub in ipList:
            #  print "[" + str(sub[0]) + "]"
        except:
            pass
        # Appender sig selv til at starte med.
        if ipList == []:
          ipList.append([myIp, time.time() + LTIMEOUT])
          message = message + " ad:" + str(myIp)
          ipLog.add(myIp)


         # Opdaterer værdier for lederen
        for sub in ipList:
          if sub[0] == myIp:
             sub[1] = time.time() + LTIMEOUT
             break
          if sub == ipList[len(ipList)-1]:
             ipList.append([myIp, time.time() + LTIMEOUT])
             message = message + " ad:" + str(myIp)
             ipLog.add(myIp)

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
            if message == "Voted":
              voteCounter += 1
              #print voteCounter
          except:
            pass
        # Bliver leder hvis der er stemmer nok til at komme ud
        # af løkken, og endnu ikke er blevet følger.
        if self.state != "follower":
          voteCounter = 0
          self.state = "leader"
          print "State set to: leader"

      elif self.state == "follower":
        # Følgeren lytter på og besvarer lederens forspørgsler,
        # samt skifter til kandidat hvis den ikke hører fra lederen.
        #print "Leader-election in:", timer - time.time()
        try:
          data, addr = sock.recvfrom(1024)
          #print "from leader:", data
          #print "noget data: " , data
          print "Parse data: " , data
          ipLog.parse(data)

          #print ipLog.getLog()
        except:
         # traceback.print_exc(file=sys.stdout)  
         pass
        try:
          message, addr = self.b_sock.recvfrom(1024)
          #print "received:", message
          ########print "Broadcast ip-address:",  addr
          #print ipLog.getLog()
          # Stemmer på kandidat hvis den modtager besked.
          # Stemmer kun 1 gang per valg.
          if message == "Vote" and tLastVote < time.time():
            tLastVote = time.time() + LTIMEOUT
            #s = socket(AF_INET, SOCK_DGRAM)
            sock.sendto("Voted", (addr[0], 5005))
          else:
            # Svarer på lederens heartbeat.
            # Opdaterer loggen
            print "broadcastbesked: ",  message
            splittext = message.split(",")
            key = splittext[0]
            msg = splittext[1]
            print msg
            ipLog.parse(msg)
            #s = socket(AF_INET,SOCK_DGRAM)
            if len(ipLog.getLog()) == 0 and ipLog.getKey() == 0:
              sock.sendto(str(-1), (addr[0], 5005))
            else:
              sock.sendto(str(ipLog.getKey()), (addr[0], 5005))
            timer = time.time() + random.uniform(2.0, 5.0)
            print "Log: ", ipLog.getLog()
            print "List: ", ipLog.getList()
 
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
