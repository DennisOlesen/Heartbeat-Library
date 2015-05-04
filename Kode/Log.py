

class log():

  def __init__(self):
   self.log = []
   self.ipList = []  
   self.key = 0
  def add(self, ip):
    self.log.append([self.key, "ad:"+ str(ip)])
    self.key += 1
    if ip not in self.ipList:
      self.ipList.append(ip)
    
    return 1

  def remove(self, ip):
    self.ipList.remove(ip)
    self.log.append([self.key, "re:" + str(ip)])
    self.key += 1

  def overwrite(self, newLog):
    #print "o1", newLog
    data = newLog.split("-") 
    #print "o2", data
    self.log = eval(data[0])
    #print "o3", self.log
    self.ipList = eval(data[1])
    #print "04", self.ipList
    self.key = self.log[len(self.log)-1][0] + 1
    #print self.ipList, self.log, self.key

  def commit(self, key):
    while(int(self.log[0][0]) <= int(key)):
      self.log.pop(0)
      if len(self.log) == 0:
         break

  def parse(self, text):
    if text[0:3] == "ow:":
      self.overwrite(text[3:])
      return

    textSplit = text.split() 

    for sub in textSplit:
      if sub[0:3] == "ad:":
        self.add(sub[3:])
      if sub[0:3] == "re:":
        self.remove(sub[3:])
      if sub[0:3] == "co:":
        self.commit(int(sub[3:]))
      if sub[0:3] == "ow:":
        self.overwrite(sub[3:])

  def getKey(self):
    return self.key 
  def getList(self):
    return self.ipList

  def getLog(self):
    return self.log
  
  def getLowestKey(self):
    return self.log[0][0]

  def compile(self,key):
    text = ""
    for sub in self.log:
      #print "test", sub, key
      if sub[0] > key:
        text = text + sub[1] + " "
    return text
