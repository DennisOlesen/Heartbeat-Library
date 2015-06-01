  #-*- coding:utf-8 -*-

# Bachelorprojekt 2015 - Heartbeat-protokollen.

from __future__ import division
from socket import *
import time, random, os, sys
import threading, Log, traceback, json

broadcast_IP = '255.255.255.255'
broadcast_PORT = 54545
LTIMEOUT = 2

print ('Sending heartbeat to IP %s, port %d.\n') % (broadcast_IP, broadcast_PORT)

class Heartbeat():
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
    #TEST variabel
    self.canbeleader = True

    self.timer = time.time() + random.uniform(2.0, 5.0)

    # Finder frem til ip-adressen for maskinen, så det virker på linux.
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("google.com", 80))
    self.myIp = (s.getsockname()[0])
    s = None

    self.ipLog = Log.log()
    self.castTimer = 0
    self.castDelay = 0.25
    self.ipList = []
    self.tLastVote = 0
    self.message = ""
    self.currentKey = -1
    self.expectedResponses = 1
    self.leaderIp = ""

    self.sock = socket(AF_INET, SOCK_DGRAM)
    self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    self.sock.bind( ("", 5005))
    self.sock.setblocking(0)

    self.start_lock = threading.Lock()
    self.update_event = threading.Condition()

    self.start_lock.acquire()
    threading.Thread(target=self.run).start()

    self.start_lock.acquire()
    self.start_lock.release()
    del self.start_lock

  def broadcast(self, data):
    """
    Sender data ud til en given broadcast IP og PORT.
    """
    self.b_sock.sendto(data, (broadcast_IP, broadcast_PORT))


  def leader(self):
    self.leaderIp = self.myIp
    # Laver ipList. hvis lederen er ny og derfor ikke har en
    if len(self.ipLog.getList()) != len(self.ipList):
       self.ipList = []
       for sub in self.ipLog.getList():
         self.ipList.append([sub, time.time() + LTIMEOUT])
    # Broadcaster med tidsinterval
    if self.castTimer < time.time():
      # Hvis der er lige så mange som forventet, comitter vi.
      #print "expected" + str(self.expectedResponses) + "responses"
      if self.expectedResponses == 0 and len(self.ipLog.getLog()) != 0 and len(self.ipList) != 1:
        self.ipLog.commit(self.currentKey)
        self.message = self.message + " co:" + str(self.currentKey)
        with self.update_event:
          self.update_event.notify_all()

      #print "Log: " ,  self.ipLog.getLog()
      #print "List: " , self.ipLog.getList()
      #print "userDic: ", self.ipLog.getUser()
      # Opdaterer loggen
      if len(self.ipList) > 1:
        self.expectedResponses = len(self.ipList)-1
      else:
        self.expectedResponses = 1
      self.broadcast(str(self.ipLog.getKey()) + "-" + self.message)
      self.currentKey = self.ipLog.getKey()
      self.message = ""
      self.castTimer = time.time() + self.castDelay
    try:
      data, addr = self.sock.recvfrom(1024)
      #modtager set fra follower.
      if (data[0:3] == "se:"):
        self.message = self.message + " " + str(self.ipLog.getKey()+1) + "," + data
        self.ipLog.parse(self.message)

      if (data[0:3] == "de:"):
        self.message = self.message + " " + str(self.ipLog.getKey()+1) + "," + data
        self.ipLog.parse(self.message)


      if (data[0:5] == "Voted") or (data[0:4] == "Vote"):
        pass
      else:
        if (int(data) > self.ipLog.getKey()+1):
           self.state = "follower"
           return
        if (int(data) >= self.currentKey):
          self.expectedResponses -= 1

        if (int(data) < int(self.ipLog.getLowestKey())):
          self.sock.sendto("ow:" + str(self.ipLog.getLog()) + "-" + str(self.ipLog.getList()) + "-" + str(self.ipLog.getUser()), (addr[0], 5005))


        if (int(data) < self.currentKey and int(data) != -1):
          # Tjekker hvis en følger er bagud, sender bagud data
          upToDateData = self.ipLog.compile(int(data))

          self.sock.sendto(upToDateData, (addr[0], 5005))

        elemNotSet = 1 # Til at checke om elementer er blevet placeret

        # Opdaterer værdier for følgerne
        for sub in self.ipList:
          if addr[0] in sub:
            sub[1] = time.time() + LTIMEOUT
            elemNotSet = 0
          if sub == self.ipList[len(self.ipList)-1] and elemNotSet:
            self.ipList.append([addr[0], time.time() + LTIMEOUT])
            self.message = self.message + " " + str(self.ipLog.getKey()+1) + ","+"ad:" + str(addr[0])
            self.ipLog.parse(self.message)

    except:
      pass
    # Appender sig selv til at starte med.
    if self.ipList == []:
      self.ipList.append([self.myIp, time.time() + LTIMEOUT])
      self.message = self.message + " " + str(self.ipLog.getKey()+1) + "," + "ad:" + str(self.myIp)
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
      voteCounter = 1.0
      self.broadcast("Vote" + " " + str(self.ipLog.getKey()))
      # Laver en voteTime, for at sikre sig at
      # den ikke venter på stemmer forevigt.
      voteTime = time.time() + LTIMEOUT
      while(voteCounter < ((len(self.ipLog.ipList))/2.0)):
        # Returnerer til følger hvis der ikke er stemmer nok
        if voteTime < time.time():
          self.state = "follower"
          voteCounter = 0.0
          self.timer = time.time() + random.uniform(2.0, 5.0)
          break
        try:
          self.message, addr = self.sock.recvfrom(1024)
          if self.message == "Voted":
            voteCounter += 1
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
    if self.ipLog.parse(data):
      with self.update_event:
        self.update_event.notify_all()

   except:
   # traceback.print_exc(file=sys.stdout)
     pass
   try:
     message, addr = self.b_sock.recvfrom(1024)
     # Stemmer på kandidat hvis den modtager besked.
     # Stemmer kun 1 gang per valg.
     if message[0:4] == "Vote" and self.tLastVote < time.time() and (int(message[5:]) >= self.ipLog.getKey()):
       self.tLastVote = time.time() + LTIMEOUT
       self.sock.sendto("Voted", (addr[0], 5005))
     else:
       self.leaderIp = addr[0]
       # Svarer på lederens heartbeat.
       # Opdaterer loggen
       try:
         key, msg = message.split("-")
       except:
         key = int(message.split("-")[1])
         msg = ""

       if self.ipLog.parse(msg):
         with self.update_event:
           self.update_event.notify_all()

       # Hvis followeren lige er startet op sender den -1 til leaderen,
       # så denne ved, at followeren skal have sendt et overwrite.
       if len(self.ipLog.getLog()) == 0 and self.ipLog.getKey() == -1:
         self.sock.sendto(str(-1), (addr[0], 5005))
       else:
         self.sock.sendto(str(self.ipLog.getKey()+1), (addr[0], 5005))
       self.timer = time.time() + random.uniform(2.0, 5.0)
       #print "Log: ", self.ipLog.getLog()
       #print "List: ", self.ipLog.getList()
       #print "userDic: ", self.ipLog.getUser()


   except:
     pass
# Bliver kandidat hvis der ikke modtages besked fra lederen.
#TEST
   if self.timer - time.time() < 0 and self.canbeleader:
     self.state = "candidate"
     print "State set to: candidate"
   time.sleep(0.5)

  def run(self):
    lck = self.start_lock

    while(True):
    # Lederen er ansvarlig for at opdatere loggen løbende via Heartbeats.
      if lck != None and len(self.leaderIp) != 0:
        lck.release()
        lck = None

      if self.state == "leader":
        self.leader()
      elif self.state == "candidate":
        self.candidate()
      elif self.state == "follower":
        self.follower()

#################################
# HER STARTER BRUGER FUNKTIONER.

  # Applikation niveau funktion, kaldes af brugeren for at sætte en værdi tilsvarende input
  def set(self, key, value):
    if self.ipLog.userDic.has_key(key) and self.ipLog.userDic[key] == value:
      return

    myJson = json.dumps({"key" : key, "value" : value}, separators=(',', ':'))

    if (self.state == "leader"):
      self.message = self.message + " " + str(self.ipLog.getKey()+1) + "," + "se:" + myJson
      self.ipLog.parse(self.message)
      with self.update_event:
        self.update_event.wait()

    if (self.state == "follower"):
      self.sock.sendto("se:" + myJson, (self.leaderIp, 5005))
      while not self.ipLog.userDic.has_key(key) or self.ipLog.userDic[key] != value:
        with self.update_event:
          self.update_event.wait()

  # Applikation niveau funktion, kaldes af brugeren for at slette en værdi tilsvarende input
  def delete(self, key):
     myJson = json.dumps({"key" : key}, separators=(',', ':'))
     if (self.state == "leader"):
       self.message = self.message + " " + str(self.ipLog.getKey()+1) + "," +"de:" + myJson
       self.ipLog.parse(self.message)
       with self.update_event:
         self.update_event.wait()

     if (self.state == "follower"):
       self.sock.sendto("de:" + myJson, (self.leaderIp, 5005))
       while self.ipLog.userDic.has_key(key):
         with self.update_event:
           self.update_event.wait()

  # Applikation niveau funktion, kaldes af brugeren for at få værdi tilsvarende input
  def get(self, key):
    if self.ipLog.userDic.has_key(key):
      return self.ipLog.userDic[key]
    return None

  def getDic(self):
    return self.ipLog.userDic

  def getState(self):
    return self.state

  def getIps(self):
    return self.ipLog.ipList
  #TEST 
  def changeState(self):
    self.canbeleader = False
    self.state = "follower"
