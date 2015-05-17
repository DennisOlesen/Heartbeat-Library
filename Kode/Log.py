import json

class log():

  def __init__(self):
   self.log = []
   self.ipList = []  
   self.key = 0
   self.userDic = {}
   
  def add(self, key, ip):
    if (len(self.log) != 0):
      if (self.log[len(self.log)-1][0] + 1) == int(key):
        self.log.append([int(key), "ad:"+ str(ip)])
        self.key += 1
        if ip not in self.ipList:
          self.ipList.append(ip)
    elif (len(self.log) == 0 and self.key == int(key)):
      self.log.append([int(key), "ad:"+ str(ip)])
      self.key += 1
      if ip not in self.ipList:
         self.ipList.append(ip)
 
  def set(self, key, data):
    myJson = json.loads(data)
    dicKey = myJson["key"]
    value = myJson["value"]
    if (len(self.log) != 0):
      if (self.log[len(self.log)-1][0] + 1) == int(key):
        self.log.append([int(key), "se:" + str(data)])
        self.key += 1
        self.userDic[dicKey] = value
    elif (len(self.log) == 0 and self.key == int(key)):
      self.log.append([int(key), "se:" + str(data)])
      self.key += 1
      self.userDic[dicKey] = value

  def delete(self, key, data):
    myJson = json.loads(data)
    dicKey = myJson["key"]
    if (len(self.log) != 0):
      if (self.log[len(self.log)-1][0] + 1) == int(key):
        self.log.append([int(key), "de:" + str(data)])
        self.key += 1
        self.userDic.pop(dicKey, None)
    elif (len(self.log) == 0 and self.key == int(key)):
      self.log.append([int(key), "de:" + str(data)])
      self.key += 1
      self.userDic.pop(dicKey, None)


  def remove(self, key, ip):
    if (len(self.log) != 0):
     if self.log[len(self.log)-1][0] + 1 == int(key):
      self.ipList.remove(ip)
      self.log.append([int(key), "re:" + str(ip)])
      self.key += 1
    elif (len(self.log) == 0 and self.key == int(key)):
      self.ipList.remove(ip)
      self.log.append([int(key), "re:" + str(ip)])
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
      try:
        key, text = sub.split(",", 1)
      except:
        key = 0
        text = sub
      if text[0:3] == "ad:":
        self.add(int(key), text[3:])
      if text[0:3] == "re:":
        self.remove(int(key), text[3:])
      if text[0:3] == "co:":
        self.commit(int(text[3:]))
      if text[0:3] == "se:":
        self.set(int(key), text[3:])
      if text[0:3] == "de:":
        self.delete(int(key), text[3:])
      
  def getKey(self):
    return self.key-1

  def getList(self):
    return self.ipList
  
  def getUser(self):
    return self.userDic

  def getLog(self):
    return self.log
  
  def getLowestKey(self):
    if len(self.log) == 0: 
      return self.key-1
    return self.log[0][0]

  def compile(self,key):
    text = ""
    for sub in self.log:
      #print "test", sub, key
      if sub[0] > key:
        text = text + str(sub[0]) + "," + sub[1] + " "
    return text
