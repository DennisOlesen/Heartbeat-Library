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
    """
    Starter heartbeat-protokollen.
    """
    self.timer = time.time() + random.uniform(2.0, 5.0)

    # Finder frem til ip-adressen for maskinen, så det virker på linux.
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("google.com", 80))
    self.myIp = (s.getsockname()[0])
    s = None

    self.ipLog = Log.log() 
    self.castTimer = 0
    self.ipList = []
    self.tLastVote = 0
    self.message = ""
    self.currentKey = -1
    self.expectedResponses = 1

    self.sock = socket(AF_INET, SOCK_DGRAM)
    self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    self.sock.bind( ("", 5005))
    self.sock.setblocking(0)

  def set(self, key, value):
    pass  


  def broadcast(self, data):
    """
    Sender data ud til en given broadcast IP og PORT.
    """
    #print "broadcast send:", data
    self.b_sock.sendto(data, (broadcast_IP, broadcast_PORT))
    #print data

  def leader(self):
    if len(self.ipLog.getList()) != len(self.ipList):
       self.ipList = []
       for sub in self.ipLog.getList():
	 self.ipList.append([sub, time.time() + LTIMEOUT])
    if self.castTimer < time.time():
      # Hvis der er lige så mange som forventet, comitter vi. 
      #print "expected" + str(self.expectedResponses) + "responses"
      if self.expectedResponses == 0 and len(self.ipLog.getLog()) != 0 and len(self.ipList) != 1:
	 print "Commiting"
	 self.ipLog.commit(self.currentKey)
	 self.message = self.message + " co:" + str(self.currentKey)
	 
      #print self.ipLog.getKey()
      print "Log: " ,  self.ipLog.getLog()
      print "List: " , self.ipLog.getList()
      # Opdaterer loggen
      if len(self.ipList) > 1:
	self.expectedResponses = len(self.ipList)-1
      else:
	self.expectedResponses = 1
      #print self.message
      self.broadcast(str(self.ipLog.getKey()) + "-" + self.message)
      #print "Key, self.message: " , self.ipLog.getKey()-1, self.message
      self.currentKey = self.ipLog.getKey()
      self.message = ""
      self.castTimer = time.time() + 0.5
    try:
      data, addr = self.sock.recvfrom(1024)
      #print "svar far hb: " , data , " ok?"
      #print "xxxxxxxxxxxxxxxxxxxxx"
      if (data == "Voted"):
	pass
      else:
	#print self.message 
	if (int(data) >= self.currentKey):
	   self.expectedResponses -= 1 
	#print "OW?: " , data, "<", self.ipLog.getLowestKey() , "ow?"
	 
	if (int(data) < int(self.ipLog.getLowestKey())): # or int(data) > self.currentKey):
	  #s = socket(AF_INET,SOCK_DGRAM)
	  #print "magic"
          print "sending ow" 
	  self.sock.sendto("ow:" + str(self.ipLog.getLog()) + "-" + str(self.ipLog.getList()), (addr[0], 5005))
	#print "self.currentKey: " , self.currentKey , " ok?"
	if (int(data) < self.currentKey and int(data) != -1):
	  #Tjekker hvis en følger er bagud, sender bagud data
	  print "Pakker upToDateData"
	  upToDateData = self.ipLog.compile(int(data))
   
	  #print "Sending", upToDateData, "..."
	  #s = socket(AF_INET,SOCK_DGRAM)
	  self.sock.sendto(upToDateData, (addr[0], 5005))
	  #print "Data er sendt: " , upToDateData
   
	elemNotSet = 1 # Til at checke om elementer er blevet placeret
   
	# Opdaterer værdier for følgerne
	for sub in self.ipList:
	  if addr[0] in sub:
	    sub[1] = time.time() + LTIMEOUT
	    elemNotSet = 0
	    #print sub
	  if sub == self.ipList[len(self.ipList)-1] and elemNotSet:
	    self.ipList.append([addr[0], time.time() + LTIMEOUT])
	    self.message = self.message + " " + str(self.ipLog.getKey()+1) + ","+"ad:" + str(addr[0])
	    #print self.message
	    self.ipLog.parse(self.message)
   
       # Printer en oversigt over IP-adresser samt
	#for sub in self.ipList:
	#  print "[" + str(sub[0]) + "]"
    except:
	pass
    # Appender sig selv til at starte med.
    if self.ipList == []:
      self.ipList.append([self.myIp, time.time() + LTIMEOUT])
      self.message = self.message + " " + str(self.ipLog.getKey()+1) + "," + "ad:" + str(self.myIp)
      #print self.message
      self.ipLog.parse(self.message)
   
   
     # Opdaterer værdier for lederen
    for sub in self.ipList:
      if sub[0] == self.myIp:
	 sub[1] = time.time() + LTIMEOUT
	 break
      if sub == self.ipList[len(self.ipList)-1]:
	 self.ipList.append([self.myIp, time.time() + LTIMEOUT])
	 self.message = self.message + " " + str(self.ipLog.getKey()+1) + ","+"ad:" + str(self.myIp)
	 self.ipLog.parse(self.message)
   
    for ip in self.ipList:
       if ip[1] < time.time():
	 self.ipList.remove(ip)
	 self.message = self.message + " " + str(self.ipLog.getKey()+1) + "," "re:" + str(ip[0])
	 self.ipLog.parse(self.message)
   
   
  def candidate(self):
     # Kandidaten er overgangsstadiet mellem følger og leder.
    # Den opretter en afstemning for at blive den nye leder.
	  # Votecounter starter på 1,
    # da en kandidat altid stemmer på sig selv.
      voteCounter = 1
      self.broadcast("Vote")
      # Laver en voteTime, for at sikre sig at
      # den ikke venter på stemmer forevigt.
      voteTime = time.time() + LTIMEOUT
      while(voteCounter <= ((len(self.ipList))/2)):
	# Returnerer til følger hvis der ikke er stemmer nok
	if voteTime < time.time():
	  self.state = "follower"
	  voteCounter = 0
	  self.timer = time.time() + random.uniform(2.0, 5.0)
	  break
	try:
	  self.message, addr = self.sock.recvfrom(1024)
	  if self.message == "Voted":
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

  
  def follower(self):
   try:
    data, addr = self.sock.recvfrom(1024)
    #print "from leader:", data
    #print "noget data: " , data
    #print "Parse data: " , data
    self.ipLog.parse(data)
  
    #print self.ipLog.getLog()
   except:
   # traceback.print_exc(file=sys.stdout)  
     pass
   try:
     message, addr = self.b_sock.recvfrom(1024)
     #print "received:", self.message
     ########print "Broadcast ip-address:",  addr
     #print self.ipLog.getLog()
     # Stemmer på kandidat hvis den modtager besked.
     # Stemmer kun 1 gang per valg.
     if message == "Vote" and self.tLastVote < time.time():
       self.tLastVote = time.time() + LTIMEOUT
       #s = socket(AF_INET, SOCK_DGRAM)
       self.sock.sendto("Voted", (addr[0], 5005))
     else:
       # Svarer på lederens heartbeat.
       # Opdaterer loggen
      # print "broadcastbesked: ",  message
       try:
	 key, msg = message.split("-")
       except:
         #print message.split("-")
         key = int(message.split("-")[1])
         msg = ""
       #print "Yoloswag"
       #print "msg: " + msg + ":msg"
      
       self.ipLog.parse(msg)
       #s = socket(AF_INET,SOCK_DGRAM)
       if len(self.ipLog.getLog()) == 0: #and self.ipLog.getKey() == 0:
         self.sock.sendto(str(-1), (addr[0], 5005))
       else:
         self.sock.sendto(str(self.ipLog.getKey()+1), (addr[0], 5005))
       self.timer = time.time() + random.uniform(2.0, 5.0)
       print "Log: ", self.ipLog.getLog()
       print "List: ", self.ipLog.getList()

   except:
     pass
# Bliver kandidat hvis der ikke modtages besked fra lederen.
   if self.timer - time.time() < 0:
     self.state = "candidate"
     print "State set to: candidate"
   time.sleep(0.5)



  def start(self):
    thread.start_new_thread(mySimpleServer, (8080,))
    while(True):
    # Lederen er ansvarlig for at opdatere loggen løbende via Heartbeats.
      if self.state == "leader":
         self.leader()
      elif self.state == "candidate":
         self.candidate()
      elif self.state == "follower":
         self.follower()
        # Følgeren lytter på og besvarer lederens forspørgsler,
        # samt skifter til kandidat hvis den ikke hører fra lederen.
        #print "Leader-election in:", timer - time.time()

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
